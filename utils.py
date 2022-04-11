

def build_image_link(image_url, height=None, width=None):
    if height is None:
        options = "1"
    else:
        options = "4, {}, {}".format(height, width)

    return "HYPERLINK(\"{}\"; IMAGE(\"{}\"; {}))".format(image_url, image_url, options)
