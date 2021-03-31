from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.UserSchema import UserSchemaOut, UserSchemaIn, UserSchemaPut
from schemas.FileSchema import PictureSchemaIn, S3PresignedUrlSchemaOut
# Models
from models.User import User, UserRoleEnum
from models.S3StaticFileClient import S3StaticFileClient

# Auth
from auth import get_current_user, has_user_read_update_perms, is_admin
from utils import serialize, validate_id_querystring
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=List[UserSchemaOut])
@validate_id_querystring
def retrieve_user_data(ids: Optional[str] = None, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # get all ids defined by query param
    if ids is None:
        return [serialize(current_user)]
    # return all user data defined in group id
    users = session.query(User).filter(User.id.in_(ids.split(','))).all()
    # if user does not belong in the organization, then do not allow access
    for user in users:
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, f"You are unauthorized to access these users as they are not in your organization")
    return [serialize(x) for x in users]


@router.put('/{user_id}')
@has_user_read_update_perms
def edit_user(user_put_body: UserSchemaPut, user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # Only super admins can edit role
    if user_put_body.role and not current_user.is_admin():
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Only admins can edit roles")
    if user_put_body.role == UserRoleEnum.super_admin and not current_user.is_super_admin():
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Only super admins can make super admins")
    # get edited user
    edited_user = session.query(User).get(user_id)
    if edited_user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"User: {user_id} doesnt exist")
    # iterate through all the attributes of the usereditschema
    for key, value in user_put_body.dict().items():
        # If key is being edited
        if value:
            setattr(edited_user, key, value)
    # push edits
    session.commit()
    return serialize(edited_user)


@router.post("")
def create_user(user: UserSchemaIn):
    new_user = User(cognito_user_id=user.cognito_user_id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    company=user.company)
    return


@router.post("/{user_id}/upload_profile_picture", response_model=S3PresignedUrlSchemaOut)
@has_user_read_update_perms
def upload_profile_picture_post(file_upload: PictureSchemaIn, user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    """Generate presigned s3 url for user to user to use to write to s3
    @returns sting: presigned s3 url

    """
    user = session.query(User).get(user_id)
    # initialize s3 client
    s3_client = S3StaticFileClient()
    # generate presigned url
    return_presigned_data = s3_client.generate_profile_picture_signed_url(
        current_user.id, file_upload.name)
    # switch profile picture
    profile_picture_url = f"{s3_client.STATIC_S3_BUCKET_NAME}/{return_presigned_data['key']}"
    user.profile_picture_url = profile_picture_url
    session.add(user)
    session.commit()
    # return presigned url
    return return_presigned_data
