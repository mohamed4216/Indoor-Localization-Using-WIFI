import numpy as np
from repository import Repository
from configuration import config
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA
from geopy.distance import vincenty
import time
import matplotlib.pyplot as plt

# Import data
repository = Repository(config)
dataset, labels = repository.get_dataset_and_labels()
dataset = dataset.fillna(-85)

# Data: Accuracy && Error
acc = []
err = []
size=[]

#Files: AccuracyBaggingDT && ErrorBaggingDT
AccuracyBaggingDT = open("AccuracyBaggingDT.txt","w")
ErrorBaggingDT = open("ErrorBaggingDT.txt", "w")

# Iterate accross the PCA dimentionality
for i in range(93,2094,100):
	print "########################"
	print "Iteration number: "+ str(i/100)
	start_time = time.time()
	size.append(i)
	# PCA number of components
	pca = PCA(n_components=i)
	
	# Apply PCA to the dataset
	pca.fit(dataset)
	dataset_new = pca.transform(dataset)

	# Split the dataset into training (90 \%) and testing (10 \%)
	X_train, X_test, y_train, y_test = train_test_split(dataset_new, labels, test_size = 0.1 )


	#Create a Bagging classifier Classifier
	cart = DecisionTreeClassifier()
	num_trees = 150
	model = BaggingClassifier(base_estimator=cart, n_estimators=num_trees)

	#Train the model using the training sets 
	model.fit(X_train, [repository.locations.keys().index(tuple(l)) for l in y_train])

	#Accuracy Output 
	accuracy = model.score(X_test, [repository.locations.keys().index(tuple(l)) for l in y_test])
	acc.append(accuracy)
	AccuracyBaggingDT.write("Size: "+ str(i)+"||Accuracy: "+str(accuracy)+"\n")
	print "Accuracy: "+str(accuracy)

	# Error Output
	Y_index_estimated= model.predict(X_test)
	Y_estimated=[repository.locations.keys()[j] for j in Y_index_estimated]
	l=[vincenty(Y_estimated[m], y_test[m]).meters for m in range(len(y_test))]
	error=sum(l) / float(len(l))
	err.append(error)
	ErrorBaggingDT.write("Size: "+str(i)+"||Error: "+str(error)+"\n")
	print "Error: "+ str(error)
	print("--- %s seconds ---" % (time.time() - start_time))
	print "########################"

AccuracyBaggingDT.close()
ErrorBaggingDT.close()

#Plot results: Accuracy and Error
plt.figure(1)
ax1 = plt.subplot(211)
ax1.title.set_text('Accuracy')
ax1.set_ylabel('Accuracy')
plt.plot(size, acc, 'b')

ax2 = plt.subplot(212)
ax2.title.set_text('Error')
ax2.set_ylabel('Error')
ax2.set_xlabel('Matrix dimensionality')
plt.plot(size,err, 'r')
plt.savefig('BaggingClassifier.png')




