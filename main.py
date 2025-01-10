import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pytubefix import YouTube
import json
import os
import subprocess
import platform

def authenticate_spotify(cid, secret):
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=cid, client_secret=secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        sp.search("test", limit=1)
        print("Authentication successful!")
        return sp
    except Exception as e:
        string = "Error Authenticating Spotify:"
        if "invalid_client" in str(e):
            print(string, "Invalid Client ID or Secret")
        else:
            print(string, e)
        return None


def get_saved_user_details():
    if os.path.exists("user_details.json"):
        with open("user_details.json", "r") as json_file:
            return json.load(json_file)
    return None


def get_user_details(user_details):
    print("-" * 50 + "\n")

    if user_details:
        default_cid = user_details["client_id"]
        default_secret = user_details["client_secret"]
        print("Local user details found")
        print("Press Enter to use the saved details")

        cid = input(f"Enter Spotify Client ID [{default_cid}]: ")
        if cid == "":
            cid = default_cid
        secret = input(f"Enter Spotify Client Secret [{default_secret}]: ")
        if secret == "":
            secret = default_secret
        return cid, secret
    else:
        cid = input("Enter Spotify Client ID: ")
        secret = input("Enter Spotify Client Secret: ")
        return cid, secret


def save_user_details(client_id, client_secret):
    user_details = {"client_id": client_id, "client_secret": client_secret}
    with open("user_details.json", "w") as json_file:
        json.dump(user_details, json_file)


def get_spotify_track_list(sp, playlist_link):
    try:
        if "open.spotify.com/playlist/" not in playlist_link:
            print("Invalid Spotify Playlist Link")
            return None

        playlist_URI = playlist_link.split("/")[-1].split("?")[0]

        print("\n" + "-" * 50)
        print("Playlist Info")
        print("Playlist Id:", playlist_URI)
        print("Playlist Name:", sp.playlist(playlist_URI)["name"])
        print("Playlist Description:", sp.playlist(playlist_URI)["description"])

        results = sp.playlist_tracks(playlist_URI)
        tracks = results["items"]
        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])

        track_info = [
            [x["track"]["name"], x["track"]["artists"][0]["name"]] for x in tracks
        ]

        print("Playlist Tracks:", len(track_info))

        return track_info
    except Exception as e:
        print("ERROR: This playlist does not exist or the url is invalid")
        return None


def get_youtube_link(song_name):
    videosSearch = VideosSearch(song_name, limit=1)
    return videosSearch.result()["result"][0]["link"]


def download_song(index, track, folder_name, total_songs):
    song_name = track[0] + " - " + track[1]
    print("Downloading Song:", song_name, f"({index+1}/{total_songs})")

    wav_file_name = os.path.join("Downloads", folder_name, f"{song_name}.wav")
    mp3_file_name = os.path.join("Downloads", folder_name, f"{song_name}.mp3")
    file_exists = os.path.exists(mp3_file_name)

    if not file_exists:
        video_link = get_youtube_link(song_name)
        video = YouTube(video_link)
        stream = video.streams.filter(only_audio=True).first()
        output_folder = os.path.join("Downloads", folder_name)

        file_name = f"{song_name}.wav"
        stream.download(output_path=output_folder, filename=file_name)

        if platform.system() == "Darwin":

            convert_to_mp3_mac(
                wav_file_name,
                mp3_file_name,
            )
            os.remove(wav_file_name)
        else:
            convert_to_mp3_windows(wav_file_name, mp3_file_name)
            os.remove(wav_file_name)
        
        print("Downloading Complete")
    else:
        print("Downloading Skipped - File Already Exists")


def convert_to_mp3_mac(file, output):
    cmd = (
        'ffmpeg -i "%s"' % file
        + ' -vn -ar 44100 -ac 2 -ab 192k -f mp3 "%s" > /dev/null 2>&1' % output
    )
    subprocess.call(cmd, shell=True)

def convert_to_mp3_windows(input_file, output_file):
    try:
        if not os.path.exists(input_file):
            print(f"Input file not found: {input_file}")
            return

        command = [
            "ffmpeg", 
            "-i", input_file, 
            "-vn",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",  
            output_file
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e.stderr.decode()}")

def main():
    print("\n" + "-" * 50)
    print("Spotify Downloader")
    print("-" * 50)

    print("\nIf you don't have a Spotify Client ID and Secret, you can get one here:")
    print("https://developer.spotify.com/dashboard/applications")
    print("Here you can create a new application to get an ID and Secret")

    test_link = (
        "https://open.spotify.com/playlist/39Z8LRUZIM3O7UAMkGpLOG?si=ccf25d5d63ff4121"
    )

    if os.path.exists(".cache"):
        os.remove(".cache")

    user_details = get_saved_user_details()
    cid, secret = get_user_details(user_details)
    sp = authenticate_spotify(cid, secret)
    if not sp:
        quit()

    if (
        (user_details is None)
        or (cid != user_details["client_id"])
        or (secret != user_details["client_secret"])
    ):
        save_details = input("Would you like to save these details locally? (y/n): ")
        try:
            if save_details.lower() == "y":
                save_user_details(cid, secret)
                print("Details saved successfully!")
        except Exception as e:
            pass

    print("-" * 50 + "\n")

    print(
        "Enter a Spotify Playlist Link in the format: https://open.spotify.com/playlist/[playlist_id]"
    )
    playlist_link = input("Enter Link: ")
    track_names = get_spotify_track_list(sp, playlist_link)

    if not track_names:
        quit()

    print("\n" + "-" * 50)

    folder_name = input("Enter Playlist Name (For Your Computer): ")
    if folder_name.replace(" ", "") == "":
        folder_name = "Playlist"

    if not os.path.exists("Downloads"):
        os.mkdir("Downloads")

    if not os.path.exists(f"Downloads/{folder_name}"):
        os.mkdir(f"Downloads/{folder_name}")

    for index, track in enumerate(track_names):
        try:
            download_song(index, track, folder_name, len(track_names))
        except KeyError:
            print("Unable to Download Song:", track[0])


if __name__ == "__main__":
    main()
