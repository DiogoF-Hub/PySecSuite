import os
import requests


# ================================================ Code =============================================================


import requests

# List of top 25 social media platforms to check in EU
SITES = {
    "Facebook": "https://www.facebook.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Twitter": "https://twitter.com/{}",
    "YouTube": "https://www.youtube.com/user/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Tumblr": "https://{}.tumblr.com",
    "WhatsApp": "https://wa.me/{}",
    "VKontakte (VK)": "https://vk.com/{}",
    "Badoo": "https://badoo.com/en/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Discord": "https://discordapp.com/users/{}",
    "Flickr": "https://www.flickr.com/photos/{}",
    "Medium": "https://medium.com/@{}",
    "Viber": "https://www.viber.com/{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Quora": "https://www.quora.com/profile/{}",
    "WeHeartIt": "https://weheartit.com/{}",
    "Periscope": "https://www.pscp.tv/{}",
    "Mix": "https://mix.com/{}",
    "Dribbble": "https://dribbble.com/{}",
    "Behance": "https://www.behance.net/{}",
}


def check_username(username):
    print(f"\n🔍 Searching for username: {username}\n")

    for platform, url in SITES.items():
        profile_url = url.format(username)
        response = requests.get(profile_url)

        if response.status_code == 200:
            print(f"✅ Found on {platform}: {profile_url}")
        else:
            print(f"❌ Not found on {platform}")


if __name__ == "__main__":
    user = input("Enter a username to search: ").strip()
    check_username(user)
