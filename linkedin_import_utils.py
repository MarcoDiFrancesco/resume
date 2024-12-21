def get_links_from_file(fname: str) -> list:
    with open(fname, "r") as file:
        links = file.readlines()
    # Remove trailing /n
    links = [link.strip() for link in links]
    return links
