# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

#retrieve shotchart data
def dataByYear(year, fileName = None):
    # Use a breakpoint in the code line below to debug your script.
    from nba_api.stats.endpoints import shotchartdetail
    import json
    import pandas as pd

    response = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=0,
        season_nullable=year,
        context_measure_simple='FGA'
    )

    content = json.loads(response.get_json())

    results = content['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    df = pd.DataFrame(rows)
    df.columns = headers
    # write to csv file
    #df.to_csv(fileName, index = False)
    return(df)

#pull positions and merge to data frame
def pullPos(fileIn, parent, fileName):

    import json
    from nba_api.stats.endpoints import commonplayerinfo
    import time
    import os.path

    #current = pd.read_csv(fileIn)

    current = fileIn

    ids = set(current['PLAYER_ID'])

    finalFrame = {}

    l = len(ids)
    i = 0

    for id in ids:
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=id)
        time.sleep(.600)
        player_info = player_info.get_normalized_dict()
        pos = player_info['CommonPlayerInfo'][0]['POSITION']
        finalFrame[id] = pos

        print(f'{i}/{l} complete \n')

        i += 1

    x = pd.DataFrame(finalFrame.items(), columns=['PLAYER_ID', 'POSITION'])

    finalFrame = x.merge(current, on = 'PLAYER_ID')

    if not os.path.isdir(parent):
        os.mkdir(parent)

    finalFrame.to_csv(fileName)

#clean multiple positions
def cleanPositions(fileIn, fileOut = None):

    # a = pd.read_csv(
    #     fileIn)
    a = fileIn

    nrow = len(a.index)

    for p in range(nrow):
        try:
            if '-' in a.POSITION[p]:
                buff = a.POSITION[p].split('-')
                a.POSITION[p] = buff[0]
        except Exception as e:
            print('error...moving on \n')

    return(a)

#run all steps of data retrieval
def dataWorkflow(year, path):
    import os.path

    stepOne = dataByYear(year)
    print('step one complete ... \n')
    stepTwo = cleanPositions(stepOne)
    print('step two complete ... \n')

    out = year+'_cleaned.csv'
    parent = os.path.join(path,year)
    fileOut = os.path.join(path, year, out)
    pullPos(stepTwo,parent,fileOut)

#create court, to be used with plot all positions
def create_court(ax, color, data, colormap, fcCol, outPath, percentile):
    # from https://towardsdatascience.com/make-a-simple-nba-shot-chart-with-python-e5d70db45d0d with minor modifications
    # Short corner 3PT lines
    ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
    ax.plot([220, 220], [0, 140], linewidth=2, color=color)

    # 3PT Arc
    ax.add_artist(
        mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Lane and Key
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))

    # Backboard
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Set axis limits
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)

    # General plot parameters
    mpl.rcParams['font.family'] = 'Avenir'
    mpl.rcParams['font.size'] = 18
    mpl.rcParams['axes.linewidth'] = 2

    hex = ax.hexbin(data['LOC_X'], data['LOC_Y'] + 60, mincnt = percentile, gridsize=(50, 50), extent=(-300, 300, 0, 940), bins = 'log', cmap=colormap)
    # Draw basketball court

    ax.set_facecolor(fcCol)
    # cb = fig.colorbar(hex, ax=ax)


    plt.savefig(outPath)

#plot each position in a dataset
def plotAllPositions(dataPath, outFolderPath, color, percentileValue):

        import os.path

        a = pd.read_csv(
            dataPath)

        posList = ['Guard', 'Forward', 'Center']

        for pos in posList:

            #filter by position, group and count
            b = a[a.POSITION == pos]

            c = b.groupby(['LOC_X', 'LOC_Y']).size().reset_index(name="count")

            c.sort_values(by=["count"], inplace=True, ascending=False)

            #find and store desired  percentile
            pFrame = np.array(c['count'])
            percentileToUse = np.percentile(pFrame, percentileValue)



            # from https://towardsdatascience.com/make-a-simple-nba-shot-chart-with-python-e5d70db45d0d
            fig = plt.figure(figsize=(4, 3.76))
            ax = fig.add_axes([0, 0, 1, 1])

            ref =  pos + '.png'

            out = os.path.join(outFolderPath, ref)

            create_court(ax=ax, color=color, data=c, colormap='YlOrRd', fcCol='black', outPath = out, percentile=percentileToUse)

            #old keeping for legacy
            #c.to_csv(outFolderPath+year+pos+'.csv')



def plotFolder(parentPath):
    import glob
    import os

    pathList = os.listdir(parentPath)

    pathList = [file for file in pathList if not file.startswith('.')]


    for folder in pathList:
        print(folder)
        os.chdir(os.path.join(parentPath,folder))
        temp = glob.glob('*.csv')
        file = os.path.join(parentPath, folder, temp[0])
        plotAllPositions(file, os.path.join(parentPath,folder), 'white', 95)
# Press the green button in the gutter to run the script.


if __name__ == '__main__':

    import pandas as pd
    import pandas as pd
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    #dataWorkflow('2017-18', '/Users/larkiniversen/Desktop/MTDA/1.Information_Design/5050Final/Data')

    plotFolder('/Users/larkiniversen/Desktop/InfoDesignProcess/Data')

    #
    # fp =  '/Users/larkiniversen/Desktop/MTDA/1.Information_Design/5050Final/Data/98/98-99_data_Positions_cleaned.csv'
    # ofp = '/Users/larkiniversen/Desktop/MTDA/1.Information_Design/5050Final/Data/98/'
    # plotAllPositions(fp, ofp, '1998-99', '#00FFFF', 90)


















