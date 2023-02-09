# python-parallel-programming

## Description

A project that explores the parallel vs. serial execution in python. The project pulls and processes a series of 10 seperate land mine detector rovers 
and their moves from a public API.  

### Part I

In Part I, the project attemps to speed up the execution time of drawing the path of the rovers based on a user-generated map.txt file that contains the dimensions
of the map and the map itself, represented as a matrix, where 0 = no mine and 1 = mine. The project then creates path_i.txt files that represent the path each
ith rover has traversed in the map.txt file. If the rover fails to dig up a mine, it will explode and end the execution for that rover.

The threading module is used to take advantage of Python parallel programming where 10 threads are spawned where each thread runs the function to draw the path.
The result is shown below:
![](Part_I_result.JPG)

### Part II, 

In Part II, the project once again attempts to speed up the execution of disarming mines whenever a rover comes across a mine. This part particularly focuses on
the computation aspect of it, and as such, everytime a rover receives a 'disarm' or 'dig' command, it will immediately disarm a mine regardless of where
it is on the map. To disarm a mine Python uuid library is used to generate a hex serial number which is then prefixed by a PIN which is further hashed using the 
SHA-256 hashing function. A mine will disarm whenever the resulting hash has a prefix of 6 leading zeros.

Since Python threading module does not allow for true parallelism due to the Global Interpreter Lock (GIL), the multiprocessing module is utilized. Processes are spawned
and contains their own GIL which effectively works around the main thread's GIL and executes each disarm command.
The result is shown below:
![](Part_II_result.JPG)
