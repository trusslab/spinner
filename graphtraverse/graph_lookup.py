import networkx as nx
# Python program to print all paths from a source to destination.

from collections import defaultdict

def printAllPathsUtil(g, u, d, visited, path):

    # Mark the current node as visited and store in path
    visited[u]= True
    u_label = g._node[u]["label"]
    u_fun_name = u_label[u_label.index("fun:")+5 : u_label.rindex("\\")]
    path.append(u_fun_name)

    # If current vertex is same as destination, then print
    # current path[]
    if u == d:
        print (path)
        return
    else:
        # If current vertex is not destination
        # Recur for all the vertices adjacent to this vertex
        for i in g[u]:
            if visited[i]== False:
                printAllPathsUtil(g, i, d, visited, path)

    # Remove current vertex from path[] and mark it as unvisited
    path.pop()
    visited[u]= False


# Prints all paths from 's' to 'd'
def printAllPaths(g, s, d):

    # Mark all the vertices as not visited
    visited = {}
    for node in g.nodes:
        visited[node] = False
    # Create an array to store paths
    path = []

    # Call the recursive helper function to print all paths
    printAllPathsUtil(g, s, d, visited, path)
    return


g = nx.drawing.nx_agraph.read_dot("callgraph_linux_2_use.dot")
print("networkx graph created")
 
s = "Node0x55f895148350" #__bpf_setsockopt
#s = "Node0x55e211e21ff0"
#d = "Node0x55e211377770" #_raw_spin_lock
#d = "Node0x55e2113b2270"
d = "Node0x55f894fd28c0" #mutex_lock
print("path is ")
printAllPaths(g,s,d)


