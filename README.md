# MSC Autoscalers Experimental
Master thesis of Job Kanis on experimental evaluation of autoscalers.

# Experimental setup

## Queries
Experiments are performed usign the following queries.

Query 1:
```
SELECT auction, DOLTOEUR(price), bidder, datetime FROM bid
```

Query 3:
```
SELECT Istream(P.name, P.city, P.state, A.id)
FROM Auction A [ROWS UNBOUNDED], Person P [ROWS UNBOUNDED] 
WHERE A.seller = P.id AND (P.state = 'OR' OR P.state = 'ID' OR P.state = 'CA');
```

Query 11:
```
SELECT bid.bidder, COUNT(*) FROM bid TIMESTAMP BY bid.datetime
GROUP BY bid.bidder, SessionWindow(seconds, 10)
```

## Auto scalers
Experiments are performed using the following auto scalers
### 1. Kubernetes HPA
The out-of-the-box horizontal pod autoscaler (HPA) form Kubernetes, configured to use CPU utilisation.

### 2. Vargav1
Autoscaler introduced by Varga et al. (2021)

### 3. Vargav2
Improved version of Vargav1, adding an additional cooldown period.

### 4. Dhalion-adapted
Custom implementation based on the Dhalion system (Floratou et al., 2017).

### 5. DS2-modern
Modern version of DS2 created by Kalavri et al. (2020)

### 6. DS2-modern-adapted
Extension of the DS2-modern autoscaler to also take into account the lag built up in the Kafka cluster

## Deployment
Experiments are originally deployed on Google Cloud.
For the original experimental setup, together with corresponding deployment files, please refer to the ./google-cloud folder.
For more information, please refer to the /google_cloud/README.md file.

## More information
For more information regarding the original experiments, please refer to the following thesis: https://repository.tudelft.nl/islandora/object/uuid:0ae72b82-b3af-4afb-a8d8-8040a226f045?collection=education