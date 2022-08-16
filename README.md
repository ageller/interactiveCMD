# interactive CMD
Testing an interactive viewer for a CMD where the user can draw a line to define the blue edge (like an isochrone).  The user can double click on a CMD to define points along a curve meant to follow the single-star sequence.  After doing so, the user can apply a selection to define the likely single members of the cluster.

To run this in a Jupyter notebook (intended purpose):

```
layout = createInteractive("filename.phot")

def bkapp(doc):
	doc.add_root(layout)

show(bkapp)
```

To run this from command line (I have only built in a hook for the file argument, but others could be added easily):
IMPORTANT: first, uncomment the two lines at the bottom of this script.  Then:

```
$ bokeh serve --show interactiveCMD.py --args filename.phot
```