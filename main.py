import json

api_file_name = input("Name of API json file: ")
api_output_file_name = input("Name of output file: ")

postman_file_path = api_file_name
with open(postman_file_path, 'r') as file:
    postman_data = json.load(file)

openapi_data = {
    "openapi": "3.0.0",
    "info": {
        "title": postman_data["info"]["name"],
        "version": "1.0.0",
        "description": "Converted from Postman Collection",
    },
    "servers": [
        {
            "url": "{{baseUrl}}"
        }
    ],
    "paths": {},
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "responses": {},
        "parameters": {},
        "schemas": {}
    },
    "security": [{"bearerAuth": []}]
}

def process_postman_items(items, paths):
    for item in items:
        if "request" in item:
            url_path = item["request"]["url"]["raw"].replace("{{baseUrl}}", "")
            method = item["request"]["method"].lower()
            if url_path not in paths:
                paths[url_path] = {}

            paths[url_path][method] = {
                "summary": item["name"],
                "description": item.get("description", ""),
                "responses": {}
            }

            if "header" in item["request"]:
                paths[url_path][method]["parameters"] = []
                for header in item["request"]["header"]:
                    paths[url_path][method]["parameters"].append({
                        "name": header["key"],
                        "in": "header",
                        "required": True if "(Required)" in header.get("description", "") else False,
                        "schema": {
                            "type": "string",
                            "default": header["value"]
                        },
                        "description": header.get("description", "")
                    })

            for response in item.get("response", []):
                response_code = str(response["code"])
                if response_code not in openapi_data["components"]["responses"]:
                    openapi_data["components"]["responses"][response_code] = {
                        "description": response["name"],
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                paths[url_path][method]["responses"][response_code] = {
                    "$ref": f"#/components/responses/{response_code}"
                }

        if "item" in item:
            process_postman_items(item["item"], paths)

process_postman_items(postman_data.get("item", []), openapi_data["paths"])

openapi_output_path = api_output_file_name
with open(openapi_output_path, 'w') as file:
    json.dump(openapi_data, file, indent=2)

openapi_output_path
