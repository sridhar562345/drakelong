def sample_spec_file(app_name):
    sample_specs_json = """{
        "swagger": "2.0",
        "host": "127.0.0.1:8000",
        "basePath": "/api/%s/",
        "info": {
            "version": "1.0.0",
            "title": "Simple API",
            "description": "A simple API to learn how to write OpenAPI Specification"
        },
        "schemes": [
            "http"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "securityDefinitions": {
            "oauth": {
                "tokenUrl": "http://auth.ibtspl.com/oauth2/",
                "flow": "password",
                "scopes": {
                    "read": "read users",
                    "write": "create users",
                    "update": "update users",
                    "delete": "delete users"
                },
                "type": "oauth2"
            }
        },
        "security": [],
        "definitions": {
            "DefaultHttpExceptionFields": {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "string"
                    },
                    "http_status_code": {
                        "type": "integer"
                    },
                    "res_status": {
                        "type": "string",
                        "enum": [
                            "DUPLICATE_TO_IDS",
                            "INVALID_INPUT_TO_IDS"
                        ]
                    }
                },
                "required": [
                    "response",
                    "http_status_code",
                    "res_status"
                ]
            },
            "TodoId": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    }
                }
            },
            "BasicTodo": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string"
                    },
                    "is_completed": {
                        "type": "boolean"
                    },
                    "remind_at": {
                        "type": "string"
                    }
                },
                "required": [
                    "description"
                ]
            },
            "Todo": {
                "allOf": [
                    {
                        "$ref": "#/definitions/BasicTodo"
                    },
                    {
                        "$ref": "#/definitions/TodoId"
                    }
                ]
            }
        },
        "parameters": {
            "TodoId": {
                "description": "todo id",
                "in": "path",
                "name": "id",
                "required": true,
                "type": "integer"
            },
            "BasicTodo": {
                "description": "Todo Parameter",
                "in": "body",
                "name": "todo",
                "required": true,
                "schema": {
                    "$ref": "#/definitions/BasicTodo"
                }
            }
        },
        "responses": {
            "SuccessResponse": {
                "description": "success response"
            }
        },
        "paths": {
            "/todos/": {
                "get": {
                    "summary": "Get all todos",
                    "description": "Returns a list containing all todos.",
                    "operationId": "get_todos",
                    "security": [
                        {
                            "oauth": [
                                "read"
                            ]
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A list of todos",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Todo"
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "404": {
                            "description": "Not Found",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        }
                    }
                },
                "post": {
                    "summary": "create a todo",
                    "description": "Create a todo",
                    "operationId": "create_todo",
                    "security": [
                        {
                            "oauth": [
                                "write"
                            ]
                        }
                    ],
                    "parameters": [
                        {
                            "$ref": "#/parameters/BasicTodo"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "create a todo",
                            "schema": {
                                "$ref": "#/definitions/TodoId"
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "404": {
                            "description": "Not Found",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        }
                    }
                }
            },
            "/todos/{id}/": {
                "parameters": [
                    {
                        "$ref": "#/parameters/TodoId"
                    }
                ],
                "post": {
                    "summary": "Get a todo",
                    "description": "Returns a todo.",
                    "operationId": "get_todo",
                    "security": [
                        {
                            "oauth": [
                                "read"
                            ]
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A todo",
                            "schema": {
                                "$ref": "#/definitions/Todo"
                            }
                        },
                        "401": {
                            "description": "Unauthorized",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "404": {
                            "description": "Not Found",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        }
                    }
                },
                "put": {
                    "parameters": [
                        {
                            "$ref": "#/parameters/BasicTodo"
                        }
                    ],
                    "summary": "Updates a todo",
                    "description": "Updates a todo.",
                    "operationId": "update_todo",
                    "security": [
                        {
                            "oauth": [
                                "update"
                            ]
                        }
                    ],
                    "responses": {
                        "200": {
                            "$ref": "#/responses/SuccessResponse"
                        },
                        "401": {
                            "description": "Unauthorized",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "404": {
                            "description": "Not Found",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Deletes a todo",
                    "description": "Deletes a todo.",
                    "operationId": "delete_todo",
                    "security": [
                        {
                            "oauth": [
                                "delete"
                            ]
                        }
                    ],
                    "responses": {
                        "200": {
                            "$ref": "#/responses/SuccessResponse"
                        },
                        "401": {
                            "description": "Unauthorized",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "403": {
                            "description": "Forbidden",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        },
                        "404": {
                            "description": "Not Found",
                            "schema": {
                                "$ref": "#/definitions/DefaultHttpExceptionFields"
                            }
                        }
                    }
                }
            }
        }
    }
    """ % app_name
    return sample_specs_json
