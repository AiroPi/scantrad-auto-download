import os
import time
import re
from glob import glob
from functools import partial

from mloader import loader
from mloader.exporter import RawExporter
import requests

try:
    from mega import Mega
    mega = Mega()
    m = mega.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    root = m.find('scans/', exclude_deleted=True)
    if not root:
        root = m.create_folder('scans')['scans']
    else:
        root = root[0]
except Exception:
    MEGA_UPLOAD = False
    print('bug')
else:
    MEGA_UPLOAD = True


INTERVAL = 60

mangas = ['one-piece']


def update_mangas():
    for manga in mangas:
        try:
            chapters = requests.get(f"https://sf.ldgr.fr/api/chapters/{manga}").json()
        except Exception:
            print(f"Error: {manga}")
            continue

        if MEGA_UPLOAD:
            parent = m.find(f"scans/{manga}/", exclude_deleted=True)
            if not parent:
                parent = m.create_folder(f"{manga}", root)[manga]
            else:
                parent = parent[0]

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

            if MEGA_UPLOAD:
                folder = m.create_folder(f"{chapter['number']}", parent)[str(chapter['number'])]

            for i, file in enumerate(sorted(glob("./tmp/*/*.jpg"))):
                os.rename(file, f"{destination}/{i}.jpg")
                if MEGA_UPLOAD:
                    mega.upload(f"{destination}/{i}.jpg", folder)

            for folder in glob("./tmp/*"):
                os.rmdir(folder)

            if os.environ["DISCORD_WEBHOOK"]:
                requests.post(os.environ["DISCORD_WEBHOOK"], json={"content": f"Nouveau chapitre {manga} ! {chapter['number']}\nGo le lire ici : {chapter['source']}"})

            print(f"New chapiter downloaded for {manga} : {chapter['number']}")


def main():
    while True:
        update_mangas()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
