Jim Rockies Overview

Jim Rockies is a quantitative sports-market analysis project focused on the mathematical analysis of sportsbook pricing, live market movement, arbitrage conditions, and asymmetric position structures.

The project treats sportsbook odds as numerical representations of market prices. Rather than focusing exclusively on predicting the outcome of a game, the system analyzes the relationship between the prices offered for different outcomes and examines how those prices change as the state of a game changes.

The project has two primary areas of analysis: arbitrage detection and position analysis.

Arbitrage analysis concerns situations in which prices available across markets create a mathematically favorable combination of positions. For a two-outcome market, the system converts the available prices into implied probabilities and evaluates their combined value. When the combined implied probability falls below 100 percent, the corresponding prices satisfy the mathematical condition for a theoretical arbitrage opportunity.

The project also analyzes situations that do not satisfy the strict arbitrage condition. In these situations, a position can still be evaluated according to its potential upside, downside, and probability of the denoted outcome. A primary position can be combined with a smaller position on the opposing outcome to modify the resulting payoff distribution. The purpose of this analysis is to determine how different allocations change the relationship between potential profit and potential loss.

This produces a distinction between two types of opportunities. The first is a direct arbitrage, where the available prices mathematically produce a positive result regardless of the outcome. The second is an asymmetric position, where one outcome is favored and the opposing position is used to reduce downside exposure without eliminating the upside of the primary position.

The system analyzes these structures mathematically rather than treating the amount placed on each outcome as an arbitrary decision. Given a primary position, opposing-market price, and available capital, the system can calculate the resulting payoff for each outcome across different hedge sizes. This allows the relationship between hedge size, retained upside, and reduced downside to be examined as a continuous range rather than as a binary hedged or unhedged decision.

A major component of the project is the analysis of live market movement. Sportsbook prices change during games as new information becomes available. Score changes, time remaining, player performance, injuries, possession, pitching situations, game state, and other observable events can cause the market price of an outcome to change.

Jim Rockies records these changes as market snapshots. A snapshot represents the state of a market at a particular point in time and can contain the game, sportsbook, timestamp, prices for each outcome, score, game state, implied probabilities, and other relevant information.

Pregame and live snapshots can then be compared mathematically. A hypothetical pregame position can be established at the initial market price, after which subsequent live prices can be evaluated to determine whether the market moved toward or away from an arbitrage threshold or whether the new prices created a more favorable asymmetric hedge.

The project therefore does not require a position to be established in order to study the market. Historical and live observations can be collected without financial execution and analyzed afterward. This allows the frequency and magnitude of potential opportunities to be measured independently of actual wagering.

The system can also monitor markets without establishing a pregame position. In this configuration, the system continuously evaluates the prices of opposing outcomes and calculates whether their combined implied probability satisfies the mathematical condition for arbitrage. This allows spontaneous arbitrage opportunities to be identified independently of any initial position.

The two forms of analysis can therefore operate simultaneously. One component evaluates whether the current market contains a direct arbitrage condition. Another evaluates how a particular position would behave under the current prices. The first is concerned with the relationship between market prices. The second is concerned with the resulting payoff distribution of a position.

The project is designed to support multiple data sources. Market information can initially be entered manually or stored in lightweight structured files. The same analytical functions can later process information obtained through APIs, public data sources, or other structured market feeds. The mathematical analysis is separated from the method used to obtain the underlying data.

The initial implementation uses Python. Market states can be represented using structured data objects containing consistent fields such as game identifier, timestamp, sportsbook, outcome prices, score, and game state. These structures can be searched and indexed using stable identifiers and can be serialized to files for later analysis.

A database is not required for the initial implementation. Lightweight file storage and in-memory data structures are sufficient for early experimentation. If the project produces a sufficiently large historical dataset, persistent storage can be introduced without changing the underlying mathematical analysis.

The first stage of the project is therefore a research and measurement system. Its purpose is to establish a collection of mathematical functions and data structures capable of representing sportsbook markets, calculating implied probabilities, identifying arbitrage conditions, modeling asymmetric positions, and comparing market states over time.

The initial system will focus on several core calculations:

* Conversion between American and decimal odds
* Implied probability calculation
* Combined implied probability
* Market overround
* Arbitrage threshold detection
* Position payoff calculation
* Hedge payoff calculation
* Profit and loss under each possible outcome
* Comparison between pregame and live prices
* Measurement of live price movement
* Identification of potential arbitrage transitions

Later versions can incorporate additional information into the analysis, including team and player statistics, injuries, lineups, historical performance, game-state variables, and internally calculated win probabilities. These components would provide an additional probability model that could be compared against the probability represented by the market price.

The project can therefore eventually analyze two separate quantities:

The price being offered by the market, and

the estimated probability of the underlying outcome.

The relationship between those quantities provides the basis for expected-value analysis. The market price determines the mathematical payoff available from a position, while the probability model determines the estimated likelihood of each outcome. Arbitrage analysis remains independent of the probability model because an arbitrage condition depends only on the available prices and their mathematical relationship.

The live component introduces a temporal dimension to the project. Instead of analyzing a market as a single pregame price, the system can treat the market as a sequence of states:


Pregame Market
      ↓
Game Begins
      ↓
Live Market State
      ↓
New Game Information
      ↓
Market Repricing
      ↓
New Live Market State
      ↓
Payoff / Arbitrage Analysis


Each state can be compared with the previous state and with the original pregame market. This creates a historical record of how prices responded to changes in the underlying event.

The resulting dataset can be used to investigate the frequency of price movements, the frequency with which markets approach or cross theoretical arbitrage thresholds, the behavior of asymmetric positions, and the relationship between market prices and independently estimated probabilities.

The project is currently focused on establishing the underlying mathematical framework and collecting market observations. Automated execution, advanced predictive models, large-scale infrastructure, and machine-learning systems are outside the initial implementation and can be considered separately after sufficient market data has been collected.

Jim Rockies is therefore structured as a quantitative research system for observing, representing, and analyzing sports-market prices and the payoff structures that result from them.

