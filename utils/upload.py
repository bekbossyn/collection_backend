import imghdr
import random
import string

from PIL import Image


def get_random_name(length=25):
    y = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(25))
    return y


def avatar_upload(instance, filename):
    """
    Returns location to saved into. Relative to MEDIA_ROOT folder in settings.
    Location format = <avatars> / <phone> / <randomfilename>.
    """
    y = get_random_name()
    return u"avatars/{}/{}.{}".format(instance.phone, y, imghdr.what(instance.avatar))


def avatar_upload_v2(instance, filename):
    """
    """
    y = get_random_name()
    return u"avatars/{}/{}.{}".format(instance.phone, y, filename)


def logo_upload_32x32(instance, filename):
    """
    Returns location to saved into. Relative to MEDIA_ROOT folder in settings.
    Location format =  /photos/ <owner_id> / <randomfilename>.
    """
    y = get_random_name()
    return u"logos/{}.{}".format(y, imghdr.what(instance.logo_32x32))


def logo_upload_64x64(instance, filename):
    """
    Returns location to saved into. Relative to MEDIA_ROOT folder in settings.
    Location format =  /photos/ <owner_id> / <randomfilename>.
    """
    y = get_random_name()
    return u"logos/{}.{}".format(y, imghdr.what(instance.logo_64x64))


def resize_image(obj, big):
    im = Image.open(obj.path)

    width, height = obj.width, obj.height

    thumb_size = 400, 400
    big_thumb_size = 800, 800

    if width > height:
       delta = width - height
       left = int(delta/2)
       upper = 0
       right = height + left
       lower = height
    else:
       delta = height - width
       left = 0
       upper = int(delta/2)
       right = width
       lower = width + upper

    im = im.crop((left, upper, right, lower))
    im.thumbnail(thumb_size, Image.ANTIALIAS)

    background = Image.new('RGB', thumb_size, (255, 255, 255, 0))
    background.paste(
        im, (int((thumb_size[0] - im.size[0]) / 2), int((thumb_size[1] - im.size[1]) / 2))
    )

    background.save(obj.path, quality=80)

    big_im = Image.open(big.path)
    big_im.thumbnail(big_thumb_size, Image.ANTIALIAS)
    big_im.save(big.path, quality=85)

