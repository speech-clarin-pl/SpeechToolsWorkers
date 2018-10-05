#include <iostream>
#include <string>
#include <stack>
#include <set>
#include "lattice.h"

using namespace std;

/**
 * Ten plik był próbą wygenerowania całej listy pełnych zdań.
 * Jest to jednak niemożliwe, gdyż ilość zdań jest wykładnicza względem ilości przejść w kracie.
 * Inaczej mówiąc, program się nigdy nie skończy (albo zajmie to 1000 lat).
 * Zostawiam tylko jako przykład przechodzenia po kracie.
 */


class IterState {
public:
	IterState(Arc* a, string s, set<int> h) :
			arc(a), sent(s), hist(h) {
	}
	Arc* arc;
	string sent;
	set<int> hist;//żeby uniknąć cykli
};

int iterate_all(string path) {
	Lattice lat;

	cout << "Loading lattice...";
	if (!lat.load(path)) {
		cout << "Error reading lattice!" << endl;
		return 0;
	} else
		cout << "DONE!" << endl;

	stack<IterState> st;

	vector<Arc*> arcs = lat.get(0);
	vector<Arc*>::iterator beg, end;
	for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++) {
		st.push(IterState(*beg, "", set<int>()));
	}

	int sent_num = 0;
	int cnt = 0;
	while (!st.empty()) {
		IterState s = st.top();
		st.pop();

		string sent = s.sent + " " + s.arc->name;
		set<int> hist = s.hist;
		hist.insert(s.arc->id);

		cnt++;
		if (cnt % 10000 == 0) {
			cout << "SN " << sent_num << " ST " << st.size() << endl;
		}

		arcs = lat.get(s.arc->end);
		if (arcs.empty()) //no states found - probably end of lattice
		{
			//cout << sent << endl;
			sent_num++;
		} else {
			for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++) {
				if (hist.find((*beg)->id) == hist.end())
					st.push(IterState(*beg, sent, hist));

			}
		}
	}

	cout << "Found " << sent_num << " sentences." << endl;

	return 0;
}

