from locust import HttpUser, task, HttpLocust, TaskSet, between, User
from locust.contrib.fasthttp import FastHttpUser
import datetime

import http

from constants import UserAuth


class GetCategory(FastHttpUser):
    token = None

    def on_request(self, request_type, name, response_time, response, **kw):
        """Перехоплює всі запити та перевіряє статуси"""
        if response.status_code == 404:
            # Якщо 404, вважаємо це успішним тестом для статистики
            self.environment.events.request_success.fire(
                request_type=request_type,
                name=name,
                response_time=response_time,
                response_length=len(response.content),
            )
        else:
            # Якщо не 404, стандартна обробка
            super().on_request(request_type, name, response_time, response, **kw)

    def on_start(self):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "password",
            "username": UserAuth.USER_EMAIL,
            "password": UserAuth.USER_PASSWORD,
            "scope": "",
            "client_id": "string",
            "client_secret": "string",
        }

        response = self.client.post("/api/auth/login", data=data, headers=headers)

        assert response.status_code == http.HTTPStatus.OK

        response_json = response.json()
        assert response_json["access_token"]
        assert response_json["refresh_token"]

        self.token = response_json["access_token"]

    @task
    def get_categories(self):
        response = self.client.get("/api/categories")
        assert response.status_code == http.HTTPStatus.OK
        response_json = response.json()
        assert isinstance(response_json["items"], list)
        assert {"items", "total", "page", "limit", "pages"} == set(response_json.keys())

    @task
    def category_flow_e2e(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        # create
        name_str = str(datetime.datetime.now())
        payload = {"name": f"{name_str} category"}
        response = self.client.post(
            "/api/categories/create", headers=headers, json=payload
        )
        assert response.status_code == http.HTTPStatus.CREATED
        response_json = response.json()
        assert {"version", "id", "created_at", "name"} == set(response_json.keys())
        category_id = response_json["id"]
        version = response_json["version"]

        # patch
        payload = {"name": f"{name_str} category and some salt", "version": version}
        response = self.client.patch(
            f"/api/categories/{category_id}", headers=headers, json=payload
        )
        assert response.status_code == http.HTTPStatus.OK
        response_json = response.json()
        assert {"version", "id", "created_at", "name"} == set(response_json.keys())
        version_new = response_json["version"]
        assert version_new == version + 1

        # get
        response = self.client.get(f"/api/categories/{category_id}", headers=headers)
        assert response.status_code == http.HTTPStatus.OK
        response_json = response.json()
        assert {"version", "id", "created_at", "name"} == set(response_json.keys())
        assert "and some salt" in response_json["name"]

        # delete
        response = self.client.delete(f"/api/categories/{category_id}", headers=headers)
        assert response.status_code == http.HTTPStatus.OK
        response_json = response.json()
        assert response_json["success"]

        # get
        response = self.client.get(f"/api/categories/{category_id}", headers=headers)
        assert response.status_code == http.HTTPStatus.NOT_FOUND
