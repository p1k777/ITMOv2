"""Functional contract and exercise containment; security regressions are student work."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sandbox import Sandbox
from service import Shop


class ShopTest(unittest.TestCase):
    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)

    def request(self, method, path, body=None, headers=None):
        with self.shop.lock:
            return self.shop.dispatch(method, path, body or {}, headers or {})

    def login(self, username="alice", password="learn-alice"):
        status, result = self.request("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": result["token"]}

    def test_health_and_catalog(self):
        self.assertEqual(self.request("GET", "/health"), (200, {"status": "ok"}))
        self.assertEqual(self.request("GET", "/products"), (200, {"chair": 5000, "lamp": 1500}))

    def test_wrong_password_rejected(self):
        self.assertEqual(self.request("POST", "/login", {"username": "alice", "password": "wrong"})[0], 401)

    def test_tokens_identify_distinct_users(self):
        alice, bob = self.login(), self.login("bob", "learn-bob")
        self.assertNotEqual(alice, bob)
        self.assertEqual(self.request("GET", "/profile?id=1", headers=alice)[1][0]["name"], "TEST_ALICE")
        self.assertEqual(self.request("GET", "/profile?id=2", headers=bob)[1][0]["name"], "TEST_BOB")

    def test_staff_can_export_with_staff_session(self):
        auth = {**self.login("staff", "learn-staff"), "X-Role": "staff"}
        status, profiles = self.request("GET", "/admin/export", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(len(profiles), 2)

    def test_own_profile_and_receipt(self):
        auth = self.login()
        status, profile = self.request("GET", "/profile?id=1", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(profile[0]["name"], "TEST_ALICE")
        status, receipt = self.request("GET", "/files?user=alice&path=receipt.txt", headers=auth)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", receipt["content"])

    def test_customer_can_buy_at_catalog_price(self):
        status, order = self.request("POST", "/orders", {"product": "lamp"}, self.login())
        self.assertEqual(status, 201)
        self.assertEqual((order["owner"], order["price"]), (1, 1500))

    def test_unknown_product_rejected(self):
        self.assertEqual(self.request("POST", "/orders", {"product": "unknown"}, self.login())[0], 400)

    def test_review_can_be_submitted_and_viewed(self):
        auth = self.login()
        self.assertEqual(self.request("POST", "/reviews", {"product": "chair", "text": "Comfortable"}, auth)[0], 201)
        self.assertIn("Comfortable", self.request("GET", "/reviews/view", headers=auth)[1])

    def test_assistant_can_return_own_receipt(self):
        auth = self.login()
        status, context = self.request("GET", "/assistant/context?order_id=1", headers=auth)
        self.assertEqual(status, 200)
        self.assertIn("chair", context["prompt"])
        status, result = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}
        }, auth)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", result["content"])

    # --- Security regression tests for REPORT_01 vulnerabilities ---

    def test_sql_injection_profile_blocked(self):
        """SQLi в /profile не должна возвращать чужие данные."""
        auth = self.login()
        # Попытка UNION-инъекции блокируется проверкой прав + параметризацией
        status, _ = self.request("GET", "/profile?id=1 UNION SELECT 1, name, email, address FROM profiles--", headers=auth)
        self.assertEqual(status, 403)
        # Легитимный запрос работает
        status, result = self.request("GET", "/profile?id=1", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(result[0]["name"], "TEST_ALICE")

    def test_sql_injection_search_blocked(self):
        """SQLi в /search не должна возвращать чужие профили."""
        auth = self.login()
        # Инъекция не возвращает чужие профили (параметризованный запрос)
        status, result = self.request("GET", "/search?q=' OR '1'='1", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(len(result), 0)
        # Легитимный поиск работает
        status, result = self.request("GET", "/search?q=TEST_ALICE", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(len(result), 1)

    def test_idor_profile_blocked(self):
        """Клиент не может читать чужой профиль (IDOR)."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Alice пытается прочитать профиль Bob
        status, _ = self.request("GET", "/profile?id=2", headers=alice)
        self.assertEqual(status, 403)
        # Bob читает свой профиль — OK
        status, profile = self.request("GET", "/profile?id=2", headers=bob)
        self.assertEqual(status, 200)
        self.assertEqual(profile[0]["name"], "TEST_BOB")

    def test_idor_staff_can_read_all_profiles(self):
        """Сотрудник может читать любые профили."""
        staff = self.login("staff", "learn-staff")
        status, profiles = self.request("GET", "/profile?id=2", headers=staff)
        self.assertEqual(status, 200)
        self.assertEqual(profiles[0]["name"], "TEST_BOB")

    def test_admin_export_requires_staff_session_not_header(self):
        """Экспорт профилей требует роль staff из сессии, а не заголовка X-Role."""
        alice = self.login("alice", "learn-alice")
        # Подмена заголовка X-Role не должна дать права staff
        status, _ = self.request("GET", "/admin/export", headers={**alice, "X-Role": "staff"})
        self.assertEqual(status, 403)
        # Реальный staff получает доступ
        staff = self.login("staff", "learn-staff")
        status, profiles = self.request("GET", "/admin/export", headers=staff)
        self.assertEqual(status, 200)
        self.assertEqual(len(profiles), 2)

    def test_files_user_isolation(self):
        """Клиент может читать только свои файлы."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Alice не может читать файл Bob
        status, _ = self.request("GET", "/files?user=bob&path=receipt.txt", headers=alice)
        self.assertEqual(status, 403)
        # Alice читает свой файл — OK
        status, receipt = self.request("GET", "/files?user=alice&path=receipt.txt", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", receipt["content"])

    def test_files_private_inaccessible(self):
        """Закрытые файлы (private/) недоступны клиентам."""
        alice = self.login("alice", "learn-alice")
        staff = self.login("staff", "learn-staff")
        # Клиент не может читать private/operator-note.txt (path traversal заблокирован)
        status, _ = self.request("GET", "/files?user=alice&path=../../private/operator-note.txt", headers=alice)
        self.assertEqual(status, 400)
        # Staff может
        status, content = self.request("GET", "/files?user=alice&path=../../private/operator-note.txt", headers=staff)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ONLY_OPERATOR_SECRET", content["content"])

    def test_debug_logs_staff_only(self):
        """Эндпоинт /debug/logs доступен только staff."""
        alice = self.login("alice", "learn-alice")
        status, _ = self.request("GET", "/debug/logs", headers=alice)
        self.assertEqual(status, 403)
        staff = self.login("staff", "learn-staff")
        status, logs = self.request("GET", "/debug/logs", headers=staff)
        self.assertEqual(status, 200)
        self.assertIsInstance(logs, list)

    def test_reviews_xss_escaped(self):
        """Текст отзыва экранируется, XSS не выполняется."""
        auth = self.login()
        self.request("POST", "/reviews", {
            "product": "chair",
            "text": "<script>alert('XSS')</script>"
        }, auth)
        status, html = self.request("GET", "/reviews/view", headers=auth)
        self.assertEqual(status, 200)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_assistant_execute_requires_auth(self):
        """Инструменты ассистента требуют валидного токена."""
        status, _ = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}
        })
        self.assertEqual(status, 401)

    def test_assistant_execute_client_read_only_own_files(self):
        """Клиент может читать только свои файлы через read_file."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Alice читает свой файл — OK
        status, content = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}
        }, alice)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", content["content"])
        # Alice не может читать файл Bob
        status, _ = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/bob/receipt.txt"}}
        }, alice)
        self.assertEqual(status, 403)
        # Staff может читать любой файл
        staff = self.login("staff", "learn-staff")
        status, content = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "read_file", "arguments": {"path": "files/bob/receipt.txt"}}
        }, staff)
        self.assertEqual(status, 200)

    def test_assistant_execute_export_profiles_staff_only(self):
        """export_profiles доступен только staff."""
        alice = self.login("alice", "learn-alice")
        status, _ = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "export_profiles", "arguments": {}}
        }, alice)
        self.assertEqual(status, 403)
        staff = self.login("staff", "learn-staff")
        status, profiles = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "export_profiles", "arguments": {}}
        }, staff)
        self.assertEqual(status, 200)
        self.assertEqual(len(profiles), 2)

    def test_assistant_execute_delete_tree_staff_only(self):
        """delete_tree доступен только staff."""
        alice = self.login("alice", "learn-alice")
        status, _ = self.request("POST", "/assistant/execute", {
            "decision": {"tool": "delete_tree", "arguments": {"path": "files/alice/receipt.txt"}}
        }, alice)
        self.assertEqual(status, 403)

    def test_assistant_context_order_ownership(self):
        """Клиент видит только свои заказы в /assistant/context."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Alice пытается увидеть заказ Bob (id=2)
        status, _ = self.request("GET", "/assistant/context?order_id=2", headers=alice)
        self.assertEqual(status, 403)
        # Alice видит свой заказ (id=1)
        status, context = self.request("GET", "/assistant/context?order_id=1", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("chair", context["prompt"])
        # Staff видит любой заказ
        staff = self.login("staff", "learn-staff")
        status, _ = self.request("GET", "/assistant/context?order_id=2", headers=staff)
        self.assertEqual(status, 200)

    def test_orders_get_own_only(self):
        """GET /orders возвращает только заказы текущего пользователя."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Создаём заказ для Bob
        self.request("POST", "/orders", {"product": "lamp"}, bob)
        # Alice видит только свои заказы
        status, orders = self.request("GET", "/orders", headers=alice)
        self.assertEqual(status, 200)
        self.assertTrue(all(o["owner"] == 1 for o in orders))
        # Staff видит все
        staff = self.login("staff", "learn-staff")
        status, orders = self.request("GET", "/orders", headers=staff)
        self.assertEqual(status, 200)
        self.assertEqual(len(orders), 3)  # 2 исходных + 1 новый от Bob

    def test_orders_get_requires_auth(self):
        """GET /orders требует аутентификации."""
        status, _ = self.request("GET", "/orders")
        self.assertEqual(status, 401)

    def test_search_client_sees_only_own_profile(self):
        """Клиент в /search видит только свой профиль."""
        alice = self.login("alice", "learn-alice")
        bob = self.login("bob", "learn-bob")
        # Alice ищет TEST_BOB — не должна найти
        status, result = self.request("GET", "/search?q=TEST_BOB", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(len(result), 0)
        # Alice ищет себя — должна найти
        status, result = self.request("GET", "/search?q=TEST_ALICE", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "TEST_ALICE")


class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox.close)

    def test_parent_paths_cannot_escape_exercise(self):
        for name in ("../../outside.txt", "/etc/passwd"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.sandbox.read(name)

    def test_external_directory_cannot_be_deleted(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            with self.assertRaises(ValueError):
                self.sandbox.delete_tree(directory)
            self.assertEqual(sentinel.read_text(), "keep")

    def test_symlink_cannot_escape_exercise(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            link = self.sandbox.root / "escape"
            link.symlink_to(directory, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.sandbox.read("escape/sentinel.txt")
            with self.assertRaises(ValueError):
                self.sandbox.delete_tree("escape")
            self.assertEqual(sentinel.read_text(), "keep")

    def test_delete_of_fixture_root_stays_inside_exercise(self):
        with TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("keep")
            self.sandbox.delete_tree(".")
            self.assertFalse(self.sandbox.root.exists())
            self.assertEqual(sentinel.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
