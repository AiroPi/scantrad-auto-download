import os
import time
import re
from glob import glob
from functools import partial
from pprint import pprint

from mloader import loader
from mloader.exporter import RawExporter
import requests

try:
    from mega import Mega
    assert "EMAIL" in os.environ
    assert "PASSWORD" in os.environ
except Exception as e:
    MEGA_UPLOAD = False
    print('Scans will not be downloaded to mega.')
    print(e)
else:
    MEGA_UPLOAD = True


INTERVAL = 60
MANGAS = ['one-piece']


class MangasAutoDownloader():
    def __init__(self):
        self.mangas = {manga: set() for manga in MANGAS}
        self.mega, self.root = self.setup_mega()

    def setup_mega(self):
        if not MEGA_UPLOAD:
            return None, None

        mega = Mega()
        mega = mega.login(os.environ['EMAIL'], os.environ['PASSWORD'])
        root = mega.find('scans/', exclude_deleted=True)
        if not root:
            root = mega.create_folder('scans')['scans']
        else:
            root = root[0]
        return mega, root

    def update_mangas(self):
        for manga in self.mangas.keys():
            try:
                chapters = requests.get(f"https://sf.ldgr.fr/api/chapters/{manga}").json()
            except Exception:
                print(f"Error: {manga}")
                continue

            if MEGA_UPLOAD:
                parent = self.mega.find(f"scans/{manga}/", exclude_deleted=True)
                if not parent:
                    parent = self.mega.create_folder(f"{manga}", self.root)[manga]
                else:
                    parent = parent[0]

            for chapter in chapters:
                destination = f"./output/{manga}/{chapter['number']}"
                
                if chapter['number'] in self.mangas[manga]:
                    continue

                if not (result := re.search(r"\d+$", chapter['source'])):
                    continue
                mangaplus_id = int(result.group(0))
                
                if MEGA_UPLOAD:
                    files = self.mega.get_files_in_node(parent)
                    present_chapters = {element['a']['n'] for element in files.values()}
                    self.mangas[manga] |= present_chapters

                    if str(chapter['number']) in self.mangas[manga]:
                        continue

                    folder = self.mega.create_folder(f"{chapter['number']}", parent)[str(chapter['number'])]
                else:
                    if os.path.isdir(destination):
                        continue
                    os.makedirs(destination)

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
                    new = os.path.join(os.path.dirname(file), f"{i}.jpg")
                    os.rename(file, new)
                    if MEGA_UPLOAD:
                        self.mega.upload(new, folder)
                        os.remove(new)
                    else:
                        os.rename(new, f"{destination}/{i}.jpg")

                for folder in glob("./tmp/*"):
                    os.rmdir(folder)

                if os.environ.get("DISCORD_WEBHOOK"):
                    requests.post(os.environ["DISCORD_WEBHOOK"], json={"content": f"Nouveau chapitre {manga} ! {chapter['number']}\nGo le lire ici : {chapter['source']}"})

                print(f"New chapiter downloaded for {manga} : {chapter['number']}")
                self.mangas[manga].add(str(chapter['number']))

    def loop(self):
        while True:
            self.update_mangas()
            time.sleep(INTERVAL)


if __name__ == "__main__":
    manga_auto_downloader = MangasAutoDownloader()
    manga_auto_downloader.loop()
