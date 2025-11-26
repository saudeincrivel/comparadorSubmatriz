import cv2 as cv
try:
    import wrapper.wrapper as wrapper
except ImportError:
    try:
        from .wrapper import wrapper
    except ImportError:
        # Fallback if we are in the root bot directory and common is a package
        from common.image_match.wrapper import wrapper

def matchImages(screen, subscreen):
    imageScreen = cv.imread(screen)
    imageSubscreen = cv.imread(subscreen)
    
    if imageScreen is None:
        print(f"Error: Could not read screen image at {screen}")
        return []
    if imageSubscreen is None:
        print(f"Error: Could not read subscreen image at {subscreen}")
        return []

    gray1 = cv.cvtColor(imageScreen, cv.COLOR_BGR2GRAY)
    gray2 = cv.cvtColor(imageSubscreen, cv.COLOR_BGR2GRAY)

    return wrapper.comparator(gray1, gray2)
