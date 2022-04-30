import os
import time
import re
from glob import glob
from functools import partial

from mloader import loader
from mloader.exporter import RawExporter
import requests

INTERVAL = 60

mangas = ['one-piece']


def update_mangas():
    for manga in mangas:
        try:
            chapters = requests.get(f"https://sf.ldgr.fr/api/chapters/{manga}").json()
        except Exception:
            print(f"Error: {manga}")
            continue

        for chapter in chapters:
            destination = f"./output/{manga}/{chapter['number']}"

            if os.path.isdir(destination):
                continue
            os.makedirs(destination)

            if not (result := re.search(r"\d+$", chapter['source'])):
                continue
            mangaplus_id = int(result.group(0))

            exporter = partial(RawExporter, destination="./tmp", title="", add_chapter_title=False)
            manga_loader = loader.MangaLoader(exporter)

            manga_loader.download(
                title_ids=None,
                chapter_ids={mangaplus_id},
                min_chapter=int(chapter['number']),
                max_chapter=int(chapter['number']),
                last_chapter=False
            )

            for i, file in enumerate(sorted(glob("./tmp/*/*.jpg"))):
                os.rename(file, f"{destination}/{i}.jpg")

            for folder in glob("./tmp/*"):
                os.rmdir(folder)

            print(f"New chapiter downloaded for {manga} : {chapter['number']}")


def main():
    while True:
        update_mangas()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
