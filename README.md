# County Ranking
![Update County Rankings](https://github.com/TrevorWinstral/County_Ranking/workflows/Update%20County%20Rankings/badge.svg)
This is to update the county ranking tables for EndCoronavirus.org, if this badge is green, then the the tables should have been updated. 

# Functionality
Using the county data from the NYT Github, the columns COVID Free days (current streak of 0 cases per day) and the Total New Cases over the last 2 weeks are calculated. Since the database isn't complete (not all counties, and some which haven't had any cases aren't reporting) we use the zero.csv for a list of said counties which are at 0 but not included. Finally the html files are written.

Vincent Brunsch (https://github.com/vbrunsch/) originally created this project, I just optimized it, added table styling, and rendered the tables into the html files.
