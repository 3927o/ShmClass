from .helpers import generate_token_info


def user_schema_signup(user):
    json_user = user.to_json()
    token_info = generate_token_info(user)
    json_user.update(token_info)
    return json_user