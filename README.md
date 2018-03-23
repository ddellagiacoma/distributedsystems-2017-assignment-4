# Byzantine Agreement

* N vessels, each general controls one vessel

* For each general (vessel)

  * Decide on a profile "honest" or "Byzantine"
  
  * For honest generals decide on a vote "attack" or "retreat"
  
  * Start the Byzantine agreement algorithm on all generals, through a webpage interface
  
* When the algorithm ends, the result and result vector should appear on each webpage (upon refresh)

  * Honest generals should agree on the same votes among them
  
  * It is not required any agreement for the Byzantine generals
  
  
## How it works

Byzantine agreement algorithm runs in two steps:

* (step 1) When voting starts:

  * Honest nodes start by sending out their votes
  
  * Byzantine nodes wait until they collect all the honest votes and send out different votes to the honest nodes in order to break agreement (if possible).
  
* (step 2) When a vessel has received all votes

    * if honest, it sends to other vessels a vector of all votes received
    
    * if Byzantine, it sends to other vessels a vector of Byzantine votes
    
* Voting and outcome:

    * When a vessel has received all the messages from step 2, it computes the (majority vote) result vector and the result
    
    * Then, it adds the result vector and the result to the webpage (to be seen upon refresh)

## Task 1 https://youtu.be/ll78bKLLGl4

* Select 4 nodes for this subtask. Using the interface set:

  * 3 honest nodes and 1 Byzantine (N=4, k=1)
  
* Demonstrate that agreement is reached. That is, no matter what the honest nodes vote for, agreement can always be reached

  * The result vectors of the honest generals should match on the entries corresponding to the honest generals
  
  * Hence, the honest generals agree on the same result.
  
* Note that the Byzantine node must respect the agreement protocol, but it can change the votes to be sent to the honest nodes (e.g. it cannot sent garbage – in this implementation, not in general)

## Task 2 https://youtu.be/7aMSQQhaOMk

* Select 3 nodes for this subtask. Using the interface set:

  * 2 honest nodes and 1 Byzantine (N=3, k=1)
  
* Set different votes for the two honest nodes. The Byzantine node must be able to convince one node to attack and another one to retreat

* The Byzantine node can only change the votes to be sent to other nodes, but always respects the agreement protocol
