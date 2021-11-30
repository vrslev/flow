from datetime import datetime
from typing import Literal, Optional

from base_vk_api import BaseVKAPI
from pydantic import BaseModel, HttpUrl

from flow.models import Post


class VKAPI(BaseVKAPI):
    def get_wall(self, *, owner_id: int):
        return self.make_request(
            method="wall.get", params={"owner_id": owner_id}, model=WallGetResponse
        )


class WallItemAttachmentPhotoSize(BaseModel):
    width: int
    height: int
    url: HttpUrl


class WallItemAttachmentPhoto(BaseModel):
    sizes: list[WallItemAttachmentPhotoSize]


class WallItemAttachment(BaseModel):
    type: str
    photo: Optional[WallItemAttachmentPhoto]


class WallItem(BaseModel):
    id: int
    owner_id: int
    marked_as_ads: Literal[0, 1]
    text: Optional[str]
    attachments: list[WallItemAttachment]
    date: datetime


class WallGetResponse(BaseModel):
    count: int
    items: list[WallItem]


def _get_photo_with_highest_quality(photo: WallItemAttachmentPhoto):
    biggest_pixel_count = 0
    url = None
    for size in photo.sizes:
        if (size.height * size.width) > biggest_pixel_count:
            url = size.url
    return url


def _parse_wall(response: WallGetResponse):
    res: list[Post] = []
    for item in response.items:
        if item.marked_as_ads:
            continue

        photos: list[HttpUrl] = []
        for attachment in item.attachments:
            if attachment.photo is None:
                continue
            if photo_url := _get_photo_with_highest_quality(attachment.photo):
                photos.append(photo_url)

        res.append(Post(id=item.id, text=item.text, photos=photos, date=item.date))
    res.sort(key=lambda post: post.date)
    return res


def get_wall(*, token: str, owner_id: int):
    response = VKAPI(token).get_wall(owner_id=owner_id)
    return _parse_wall(response)
