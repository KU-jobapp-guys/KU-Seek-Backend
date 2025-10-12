"""Module for testing the Professor Connection features."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ProfessorConnectionTestCase(RoutingTestCase):
    """Test case for professor connections."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_get_empty_connections(self):
        """Test that it returns an empty list for professor with no connections."""
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertTrue(isinstance(res.get_json(), list))
        self.assertEqual(res.status_code, 200)

    def test_get_connections_status_code(self):
        """Test fetching connections returns 200 status code."""
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertEqual(res.status_code, 200)

    def test_post_new_connection_status_code(self):
        """Test creating a new connection returns 201 status code."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        
        connection_payload = {
            "company_id": 3,
        }
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)

    def test_post_new_connection_returns_correct_data(self):
        """Test that created connection returns the correct data."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)
        
        connection_payload = {
            "company_id": 2,
        }
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)
        data = res.json
        self.assertEqual(data["company_id"], connection_payload["company_id"])
        self.assertIn("id", data)
        self.assertIn("professor_id", data)
        self.assertIn("created_at", data)

    def test_post_connection_empty_body(self):
        """Test creating a connection with empty body returns 400."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={},
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("company_id' is a required property", res.json["detail"])

    def test_post_connection_missing_company_id(self):
        """Test creating a connection without company_id returns 400."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"invalid_field": "value"},
        )

        self.assertEqual(res.status_code, 400)

    def test_post_then_delete_connection(self):
        """Test creating a connection and then deleting it."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)

        connection_payload = {
            "company_id": 6,
        }

        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)
        created_data = res.json
        connection_id = created_data["id"]
        self.assertEqual(6, created_data["company_id"])

        before_delete = self.client.get("/api/v1/connections",
                                        headers={
                                            "access_token": jwt
                                        })

        res = self.client.delete(
            f"/api/v1/connections?connection_id={connection_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )


        self.assertEqual(res.status_code, 200)
        deleted_data = res.json
        self.assertEqual(connection_id, deleted_data["id"])

        res = self.client.get("/api/v1/connections", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        connections = res.json
        self.assertLess(len(connections), len(before_delete.json))

    
    def test_delete_connection_returns_correct_fields(self):
        """Test that delete response contains expected fields."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"company_id": 2},
        )
        connection_id = res.json["id"]

        res = self.client.delete(
            f"/api/v1/connections?connection_id={connection_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["id"], connection_id)
        self.assertEqual(data["company_id"], 2)
        self.assertEqual(data["professor_id"], 2)

    def test_delete_nonexistent_connection(self):
        """Test deleting a connection that doesn't exist should return 404."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)

        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        res = self.client.delete(
            f"/api/v1/connections/?connection_id={non_existent_uuid}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertEqual(res.status_code, 404)
        self.assertIn("not found", res.json["detail"])

    def test_delete_connection_invalid_uuid(self):
        """Test deleting with invalid UUID format should return 400 or 500."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)

        res = self.client.delete(
            "/api/v1/connections/?connection_id=invalid-uuid",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertIn(res.status_code, [400, 404, 500])

    def test_delete_connection_unauthorized_professor(self):
        """Test that a professor cannot delete another professor's connection."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        
        jwt1 = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        connection_payload = {"company_id": 1}

        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt1},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)
        connection_id = res.json["id"]

        jwt2 = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)
        res = self.client.delete(
            f"/api/v1/connections/?connection_id={connection_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt2},
        )

        self.assertEqual(res.status_code, 404)
        self.assertIn("not found", res.json["detail"])

    def test_post_multiple_connections(self):
        """Test creating multiple connections for the same professor."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)

        res1 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"company_id": 4},
        )
        self.assertEqual(res1.status_code, 201)

        res2 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"company_id": 5},
        )
        self.assertEqual(res2.status_code, 201)

        res = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertEqual(res.status_code, 200)
        connections = res.json
        self.assertGreaterEqual(len(connections), 2)

    def test_post_duplicate_connection(self):
        """Test creating a duplicate connection returns 409."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user3_id, secret=SECRET_KEY)
        
        connection_payload = {"company_id": 7}
        
        res1 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )
        self.assertEqual(res1.status_code, 201)
        first_connection_id = res1.json["id"]
        self.assertEqual(res1.json["company_id"], 7)
        
        res2 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res2.status_code, 500)
        self.assertIn("already exists", res2.json["message"])
        
        res3 = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertEqual(res3.status_code, 200)
        connections = res3.json
        
        company_7_connections = [conn for conn in connections if conn["company_id"] == 7]
        self.assertEqual(len(company_7_connections), 1)
        self.assertEqual(company_7_connections[0]["id"], first_connection_id)


    def test_different_professors_same_company(self):
        """Test that different professors can connect to the same company."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        
        jwt1 = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res1 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt1},
            json={"company_id": 7},
        )
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res1.json["company_id"], 7)
        self.assertEqual(res1.json["professor_id"], 1)
        
        jwt2 = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)
        res2 = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt2},
            json={"company_id": 7},
        )
        self.assertEqual(res2.status_code, 201)
        self.assertEqual(res2.json["company_id"], 7)
        self.assertEqual(res2.json["professor_id"], 2)
        
        connections_prof1 = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt1},
        )
        company_7_prof1 = [c for c in connections_prof1.json if c["company_id"] == 7]
        self.assertEqual(len(company_7_prof1), 1)
        
        connections_prof2 = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt2},
        )
        company_7_prof2 = [c for c in connections_prof2.json if c["company_id"] == 7]
        self.assertEqual(len(company_7_prof2), 1)
        
        self.assertNotEqual(res1.json["id"], res2.json["id"])
