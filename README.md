# lines2anki

Anki add-on for importing lines of movie and TV series as new notes, composed by audio media and subtitle. You should prepare separated audio and lyric files previously, using tools such as Aboboo. Personally I write this add-on to import Aboboo sentence library.

Much thanks to [hssm](https://github.com/hssm/media-import), from whom I mocked the structure of programme.

![Link to add-on]()

---

This add-on will allow you to import audio files with lyric(.lrc) into your Anki collection, and use their filename as a component of the note.

When the add-on is installed, a `Lines Import...` option will be added to the `Tools` menu.

![Menu]()

Before you do importing, you are supposed to organize the files first. Firstly put audio files as well as lyric files (with the same name) into the same folder. Rename the folder as the provenance of the audio. Optionally you can add several pictures into the folder, the add-on can select a random one from them as a part of the note.

We will use an example file tree like below:

```bash
Spam and Eggs
|___ ham-a.mp3
|___ ham-a.lrc
|___ ham-j.mp3
|___ eggs.jpeg
```

Back to Anki, selecting the menu item will open the Audio Import window.

![SettingsWidget]()

From this window, you are able to:

- Browse and select the folder where files are located
- Change provenance
- Choose which deck to import into
- Choose which note type to use for the imported notes
- Decide the content for each field
- Add tags for all the imported notes

After accepted, all the audio and image files will be imported into media.collection, with standardized filename. New filename is composed by the provenance (which is the folder name by default, with all spaces replaced by dots) and timestamp (which makes the filename unique). Like this:

```bash
collection.media
|___ Spam.and.Eggs.audio-1587037400.150538(1).mp3
|___ Spam.and.Eggs.audio-1587037400.179473(2).mp3
|___ Spam.and.Eggs.image-1587037400.1434484.jpeg
```

Here is a list of the content available to insert into fields.

- Filename :     The name of the file including the extension (`Spam.and.Eggs.audio-1587037400.150538(1).mp3`)
- Provenance :   The origin of the lines, such as the title of movies. When you choose a new folder, it will be automatically changed to the folder's name (`Spam and Eggs`) You can also modify it manually.
- Audio :        The audio file itself (`[sound:Spam.and.Eggs.audio(1).mp3]`)
- Subtitle :     The lyric that stored in .lrc files
- Random Image : A random image file in the folder. (`<img src="Spam.and.Eggs.image-1587037400.1434484.jpeg">`)

All the new generated cards are added to the selected deck.

![Complete]()

## Developing Guidance

This is my very first try on writing Anki Add-ons. It's not that enjoyable but worth the time  <(￣︶￣)>

### Developing Environment

- Operate system    Windows 10
- IDE               Pycharm, Visual Studio Code (used for viewing .log files)
- Python            Python 3.8
- Anki              Anki 2.1

### Mistakes I've made

1. To call the function when its signal triggered

   ```py
   action = QAction("Voice Clips Import", mw)
   # Right
   action.triggered.connect(do_function)
   # Wrong
   action.triggered.connect(do_function())
   ```
