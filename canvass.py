'''
James Gao
January 3, 2019

This program reads text output from an election canvass and exports it to a 
CSV file. It is designed to work for Warren County Ohio General Election results
but may also function well with similarly formatted results.

Example usage:
"warren_18.txt" is the textfile containing Warren County's 2018 general election
results. The textfile must be in the current directory.

There are two functions that will useful for the user. They are display_contests and 
gen_election_table. Run these functions with the appropriate inputs to convert election
results.

display_contests("warren_18.txt") returns all the separate electoral contests and an
index number used to retrieve results for that contest.

gen_election_table("warren_18.txt", 6, "senate_2018.csv") reads the textfile 
warren_18.txt with the election results, looks at the sixth contest (the U.S Senate 
race), and outputs the results to a CSV file called "senate_2018.csv"

There are five other functions defined in this script. They are: read_canvass_from_text, 
grab_contest_title, grab_candidates, verify_precincts, and grab_precincts. The user need
not run these functions; they are run internally by the program.

Warren County election results are at 
https://www.warrencountyboe.us/results/VotingResults/default.aspx?filename=votingpublish.rpt
'''

import re 
import csv

def read_canvass_from_text(import_filepath):
    '''
    Reads the election canvass from a textfile and separates it by electoral 
    contest
    Inputs:
        import_filepath: (string) the path for the textfile containing the 
        canvass
    Output:
        contests: (list of strings)
    '''
    with open(import_filepath, 'r') as canvass_text:
        canvass = canvass_text.read()
        contests = re.split(r"={2,}", canvass)
        if contests[-1] == "":
            del contests[-1]
    return contests

def grab_contest_title(contest):
    '''
    Finds the name of the electoral contest from a string containing the contest
    results
    Inputs:
        contest: (string) the results canvass for a particular contest
    Output:
        contest_title: (string)
    '''
    contest = contest.splitlines()
    contest_title = None
    found_title = False
    k = 0
    #Look for the first line with the word VOTES, the line with the contest title
    #is the line that follows immediately afterwards
    while not found_title and k < 10000:
        if "VOTES" in contest[k].upper():
            contest_title = contest[k+1].rstrip()
            #Checks whether contest title spills out into second line
            if "vote for not more" in contest[k + 2].lower():
                found_title = True
            else:
                contest_title = (contest_title + " " + 
                    contest[k + 2].lstrip().rstrip())
                found_title = True
        else:
            k = k + 1
    return contest_title

def grab_candidates(contest):
    '''
    Finds the candidates (including overvotes and undervotes) from a string
    containing the contest results
    Inputs:
        contest: (string) the results canvass for a particular contest
    Output:
        candidates: (dictionary of strings)

    '''
    candidates = {}
    candidates_wspace = re.findall(r"(\d{2}\s=\s[a-zA-z/\s().'\-]+)", contest)
    for candidate in candidates_wspace:
        candidate = candidate.rstrip()
        candidate = candidate.split(" = ")
        candidate_index = int(candidate[0])
        candidate_name = candidate[1]
        candidates[candidate_index] = candidate_name
    return candidates

def verify_precincts(contest):
    '''
    Removes all lines except those corresponding to precinct results
    Inputs:
        contest: (string) the results canvass for a particular contest
    Outputs:
        contest_cleaned: (list of strings)
    '''
    contest = contest.splitlines()
    found_first_precinct = False
    k = 0
    #Look for the first line corresponding to a precinct
    while not found_first_precinct:
        test = re.findall(r"^\d{4}\s\d{0,4}\s?[a-zA-z]+", contest[k])
        if len(test) > 0:
            found_first_precinct = True
            contest_cleaned = contest[k:]
        elif k < 10000:           
            k = k + 1
        else:
            contest_cleaned = []
    return contest_cleaned

def grab_precincts(contest):
    '''
    Outputs the results by precinct for a given electoral contest
    Inputs:
        contest: (string) the results canvass for a particular contest
    Outputs:
        precinct_results: (list of strings)
    '''
    contest_cleaned = verify_precincts(contest)
    precinct_results = []
    for precinct in contest_cleaned:
        primary_id = None
        secondary_id = None
        precinct = re.split(r"\s{2,}", precinct)
        precinct_descrip = re.split(r"\d{4}\s", precinct[0])[-1]
        precinct_votes_str = precinct[1:]
        precinct_votes = []
        for vote in precinct_votes_str:
            vote = int(vote)
            precinct_votes.append(vote)
        precinct_ids = re.findall(r"\d{4}", precinct[0])
        #Some precincts have one ID, some have two
        if len(precinct_ids) >= 1:
            primary_id = precinct_ids[0]
            if len(precinct_ids) >= 2:
                secondary_id = precinct_ids[1]
        precinct_result = [primary_id, secondary_id, precinct_descrip]
        precinct_result = precinct_result + precinct_votes
        precinct_results.append(precinct_result)
    return precinct_results

def display_contests(import_filepath):
    '''
    Reads the canvass textfile and displays a dictionary of contests by
    index number
    Inputs:
        import_filepath: (string) the path for the textfile containing the 
        canvass
    Outputs:
        titles_dict: (dictionary)    
    '''
    contests = read_canvass_from_text(import_filepath)
    titles_dict = {}
    for k in range(1, len(contests)):
        contest_title = grab_contest_title(contests[k])
        if contest_title not in titles_dict:
            titles_dict[contest_title] = k
        else:
            titles_dict[str(contest_title + str(k))] = k
    return titles_dict

def gen_election_table(import_filepath, contest_number, export_filepath = None):
    '''
    Generates a table of results for a given contest. If export_filepath is given,
    exports results to a CSV file. Use the display_contests function to find the
    contest_number for a given race.
    Inputs:
        import_filepath: (string) the path for the textfile containing the 
        canvass
        contest_number: (int) numerical index for an electoral contest
    Outputs:
        table (list of lists of strings/ints)
    '''
    print("At contest number " + str(contest_number))
    contests = read_canvass_from_text(import_filepath)
    assert contest_number < len(contests), "Contest number too large. \
        No contest exists for given contest number."
    contest = contests[contest_number]
    title = grab_contest_title(contest)
    candidates = grab_candidates(contest)
    precinct_results = grab_precincts(contest)
    title_header = [title]
    header = ["Primary precinct ID", "Secondary precinct ID", "Precinct name"]
    for k in (range(1, len(candidates) + 1)):
        header.append(candidates[k])
    if export_filepath:
        with open(export_filepath, "w", newline = "") as csvfile:
            precinctwriter = csv.writer(csvfile, delimiter = ',', 
                quotechar = '"', quoting = csv.QUOTE_ALL)
            precinctwriter.writerow(title_header)
            precinctwriter.writerow(header)
            for row in precinct_results:
                precinctwriter.writerow(row)
    else:
        table = []
        table.append(title_header)
        table.append(header)
        for row in precinct_results:
            table.append(row)
        return table
