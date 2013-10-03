import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt


def plotAlphaGamma():


    # for gamma in gammas:
    data = np.genfromtxt('outputPhrasesHistogram'+
            '.csv', delimiter=',', names=['x', 'y'])
    data2 = np.genfromtxt('outputPhrasesHistogram'+
            '.csv', delimiter=',', names=['x', 'y'])
    """
    plt.xlabel('Index of the jump')
    plt.ylabel('Number of occurrences')
    plt.title('Histogram reordering')
    plt.hist(data['x'], data['y'])
    """
    
   
    xx=data['x']
    yy=data['y']
    xx2=data2['x']
    yy2=data2['y']
    N = len(xx)
    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, yy, width, color='r')
    
    
    rects2 = ax.bar(ind+width, yy2, width, color='y')
    
    # add some
    ax.set_ylabel('Scores')
    ax.set_title('Scores by group and gender')
    ax.set_xticks(ind+width)

    ax.set_xticklabels( xx )
    
    ax.legend( (rects1[0], rects2[0]), ('clean', 'web') )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    
    plt.show()
    




plotAlphaGamma()

