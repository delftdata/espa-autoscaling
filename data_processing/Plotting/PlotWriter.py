import os


def savePlot(plt, saveDirectory, saveName, bbox_inches=None, dpi=None):
    if not os.path.exists(saveDirectory):
        print(f"Creating save-directory {saveDirectory}")
        os.makedirs(saveDirectory)
    fileLocation = f"{saveDirectory}/{saveName}.png"
    plt.savefig(fileLocation, bbox_inches=bbox_inches, dpi=dpi)
    print(f"Saved graph at: {fileLocation}")

    plt.close()


def showPlot(plt):
    plt.show()
