import os
import imageMatcher

large_image_path = os.path.join(os.path.dirname(__file__),"..", "..", "data", "screen", "current_screen.png")
small_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "assets", "img_chrome_profile_settings.png")
matches = imageMatcher.matchImages(large_image_path, small_image_path)


if len(matches) > 0:
    print(matches)
else:
    print("No matches found")
print(matches)