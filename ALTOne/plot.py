import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt


def plotHistogramOfOccurrences(name1,name2,title):


    # for gamma in gammas:
    data = np.genfromtxt('outputs\\'+name1+
            '.csv', delimiter=',', names=['x', 'y'])
    data2 = np.genfromtxt('outputs\\'+name2+
            '.csv', delimiter=',', names=['x', 'y'])
    """
    plt.xlabel('Index of the jump')
    plt.ylabel('Number of occurrences')
    plt.title('Histogram reordering')
    plt.hist(data['x'], data['y'])
    """
   
    xxFloat=data['x']
    yy=data['y']
    xx2=data2['x']
    yy2=data2['y']
    N = len(xx2)
    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, yy, width, color='r')
    
    
    rects2 = ax.bar(ind+width, yy2, width, color='y')
    
    # add some
    ax.set_ylabel('% of occurrence')
    ax.set_title(title)
    ax.set_xticks(ind+width)
    xx=len(xxFloat)*[0]
    for i in range(len(xxFloat)):
        xx[i]=int(xxFloat[i])
    ax.set_xticklabels( xx )
    
    ax.legend( (rects1[0], rects2[0]), ('clean', 'web') )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            #ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
            #        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)   
    plt.show()
    
    
clean='clean.output'
web='web.output'   
plotHistogramOfOccurrences(clean+'PhrasesHistogram', web+'PhrasesHistogram','Histogram of occurrences of phrases based orientations')
plotHistogramOfOccurrences(clean+'WordsHistogram', web+'WordsHistogram','Histogram of occurrences of words based orientations')
plotHistogramOfOccurrences(clean+'distance_phrases', web+'distance_phrases', 'Histogram of occurrences of distances between phrases')
plotHistogramOfOccurrences(clean+'distance_words', web+'distance_words', 'Histogram of occurrences of distances between phrases and words')
