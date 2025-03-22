from fastapi import Depends, HTTPException, Request
import httpx

from services.api import get_user_by_access_token, get_new_token_pair


async def get_current_user_with_tokens(request: Request):
    access_token = request.cookies.get("access_token") or ""
    refresh_token = request.cookies.get("refresh_token") or ""
    user = None

    if not access_token and not refresh_token:
        return None
    if access_token:
        user = await get_user_by_access_token(access_token)

    if user:
        user["access_token"] = access_token
        user["refresh_token"] = refresh_token
        return user

    if not refresh_token:
        return None

    new_token_pairs = await get_new_token_pair(refresh_token)
    user = await get_user_by_access_token(new_token_pairs.get("access_token") or "")
    user |= new_token_pairs

    return user
