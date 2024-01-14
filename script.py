import spotipy
from spotipy.oauth2 import SpotifyOAuth

def authenticate_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='a4a2adb3d3ac44d6be8a8076fa0f8a36', client_secret='c24eae8c4331418fb0ceb0529533a27e', redirect_uri='http://localhost:8888/callback', scope='playlist-read-private,playlist-read-collaborative,playlist-modify-private,playlist-modify-public'))

def get_all_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def remove_common_songs(sp, playlist_id, common_songs):
    common_song_list = list(common_songs)
    for i in range(0, len(common_song_list), 100):
        batch = common_song_list[i:i+100]
        sp.playlist_remove_all_occurrences_of_items(playlist_id, batch)

def get_all_user_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()
    playlists.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        playlists.extend(results['items'])
    return playlists

def main():
    sp = authenticate_spotify()

    print("Fetching all user's playlists...")
    all_playlists = get_all_user_playlists(sp)

    # Display user's playlists
    print("\nYour playlists:")
    for i, playlist in enumerate(all_playlists):
        print(f"{i + 1}. {playlist['name']}")

    # Ask user to choose playlists
    playlist1_index = int(input("Enter the number of the first playlist to compare: ")) - 1
    playlist2_index = int(input("Enter the number of the second playlist to compare: ")) - 1

    playlist1_id = all_playlists[playlist1_index]['id']
    playlist2_id = all_playlists[playlist2_index]['id']

    # Get all tracks from the selected playlists
    playlist1_tracks = get_all_tracks(sp, playlist1_id)
    playlist2_tracks = get_all_tracks(sp, playlist2_id)

    # Extract track IDs for comparison
    playlist1_track_ids = set()
    for track in playlist1_tracks:
        try:
            if track.get('track'):
                playlist1_track_ids.add(track['track']['id'])
        except (KeyError, TypeError):
            print(f"Error extracting track ID for Playlist 1 Track: {track}")

    playlist2_track_ids = set()
    for track in playlist2_tracks:
        try:
            if track.get('track'):
                playlist2_track_ids.add(track['track']['id'])
        except (KeyError, TypeError):
            print(f"Error extracting track ID for Playlist 2 Track: {track}")

    # Find common songs
    common_songs = set(playlist1_track_ids) & set(playlist2_track_ids)

    if common_songs:
        print(f"\nRemoving {len(common_songs)} common songs from which playlist?")
        print("1. First playlist")
        print("2. Second playlist")
        print("3. Both playlists")

        remove_option = int(input("Enter the number of the playlist(s) to remove common songs from: "))

        if remove_option == 1:
            remove_common_songs(sp, playlist1_id, common_songs)
            print("Common songs removed from the first playlist.")
        elif remove_option == 2:
            remove_common_songs(sp, playlist2_id, common_songs)
            print("Common songs removed from the second playlist.")
        elif remove_option == 3:
            remove_common_songs(sp, playlist1_id, common_songs)
            remove_common_songs(sp, playlist2_id, common_songs)
            print("Common songs removed from both playlists.")
        else:
            print("Invalid input. No changes made.")
    else:
        print("No common songs found.")

if __name__ == "__main__":
    main()