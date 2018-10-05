#include <fstream>
#include <sstream>
#include <set>
#include <stack>
#include <cassert>
#include <algorithm>
#include "lattice.h"

using namespace std;

Lattice::Lattice() {
	state_num = 0;
	last_state = 0;
	state = NULL;
}

Lattice::~Lattice() {
	if (state != NULL)
		delete[] state;
}

bool Lattice::save_wordlist(string name) {
	ofstream file(name.c_str());
	if (file.fail())
		return false;

	set<string> words;

	vector<Arc>::iterator beg, end;
	for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++)
		words.insert((*beg).name);

	set<string>::iterator beg2, end2;
	for (beg2 = words.begin(), end2 = words.end(); beg2 != end2; beg2++)
		file << (*beg2) << endl;
	file.close();

	return true;
}

bool Lattice::load(string path) {
	ifstream file(path.c_str());

	if (file.fail())
		return false;

	string line;

	getline(file, name);

	while (true) {
		getline(file, line);

		try {
			Arc arc(arcs.size(), line);
			arcs.push_back(arc);

			if (state_num < arc.start)
				state_num = arc.start;
			if (state_num < arc.end)
				state_num = arc.end;
		} catch (ios::failure & f) {
			stringstream sstr(line);
			sstr >> last_state;
			break;
		}
	}

	file.close();

	state = new vector<Arc*> [state_num];

	vector<Arc>::iterator beg, end;
	for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++) {
		(*beg).state_off = -1;
		state[(*beg).start].push_back(&(*beg));
	}

	stack<Arc*> st;
	vector<Arc*>::iterator pbeg, pend;
	for (pbeg = state[0].begin(), pend = state[0].end(); pbeg != pend; pbeg++) {
		(*pbeg)->state_off = 0;
		st.push(*pbeg);
	}

	while (!st.empty()) {
		Arc* a = st.top();
		st.pop();

		if (a->end < 0 || a->end >= state_num)
			continue;

		for (pbeg = state[a->end].begin(), pend = state[a->end].end();
				pbeg != pend; pbeg++) {
			if ((*pbeg)->state_off < 0) {
				(*pbeg)->state_off = a->state_off + a->state_len;
				st.push(*pbeg);
			} else {
				//assert((*pbeg)->state_off == a->state_off + a->state_len);
			}

		}
	}

	return true;
}

vector<Arc*> Lattice::get(int s) {

	if (s >= state_num || s < 0) {
		return vector<Arc*>();
	}

	return state[s];
}

vector<Arc*> Lattice::get(bool (*comp)(Arc*, void*), void* arg) {
	vector<Arc*> ret;
	vector<Arc>::iterator beg, end;
	for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++) {
		if (comp(&(*beg), arg))
			ret.push_back(&(*beg));
	}
	return ret;
}

Arc::Arc(int id, string line) {
	stringstream sstr(line);
	sstr.exceptions(istream::failbit | istream::badbit);

	this->id = id;

	start = 0;
	end = 0;
	name = "";
	w_a = 0;
	w_b = 0;
	state_len = 0;
	state_off = 0;

	sstr >> start >> end >> name >> w_a;
	sstr.ignore(1);
	sstr >> w_b;
	int pos = sstr.tellg();
	state_len = 1;
	for (string::iterator iter = line.begin() + pos; iter != line.end(); iter++)
		if (*iter == '_')
			state_len++;
}

string Arc::toString() {
	stringstream sstr;
	sstr << name << " (" << start << "->" << end << ") [" << w_a << "," << w_b
			<< "] l=" << state_len << " o=" << state_off;
	return sstr.str();
}

class sortitem {
public:
	double val;
	Arc* arc;
	bool operator<(sortitem& item) {
		return val > item.val;
	}
};

vector<Arc*> nbest(vector<Arc*> arcs, int n) {

	vector<sortitem> vec;

	vector<Arc*>::iterator beg, end;
	for (beg = arcs.begin(), end = arcs.end(); beg != end; beg++) {
		sortitem si;
		si.arc = *beg;
		si.val = (*beg)->w_a + (*beg)->w_b;
		vec.push_back(si);
	}

	sort(vec.begin(), vec.end());

	set<string> vite;

	arcs.clear();
	for (size_t i = 0; i < vec.size(); i++) {
		Arc* a = vec[i].arc;

		stringstream sstr;
		sstr << a->name << a->end;
		string h = sstr.str();

		if (vite.find(h) == vite.end()) {
			vite.insert(h);
			arcs.push_back(a);
		}
	}

	if (n > 0 && n < (int) arcs.size() - 1) {
		arcs.erase(arcs.begin() + n, arcs.end());
	}

	return arcs;
}
