#include <iostream>
#include <fstream>
#include <string>
#include <stack>
#include <set>
#include <list>
#include <algorithm>
#include <cmath>
#include "lattice.h"
#include "Lexicon.h"

using namespace std;

/**
 * Pomocnicza klasa reprezetnująca hipotezę zwracaną przez program.
 */
class Hypo {
public:

	string word; //wyraz zrobiony ze sklejenia kliku sąsiednich tokenów w kracie
	Trans trans; //transkrypcja powyższego wyrazu
	int start; //początek wyrazu (w ramkach; zwykle 100 ramek/s)
	int len; //długość wyrazu
	double w; //miara  jakości/prawdopodobieństwo

	Hypo() :
			start(-1), len(0), w(0) {
	}

	//potrzebne do sortowania według prawdopodobieństwa
	bool operator<(Hypo & other) {
		return w > other.w;
	}

	//odległość hipotez od siebie w czasie
	//TODO: jest to zrobione w mało przemyślany sposób - warto przemyśleć czy jest lepszy sposób
	//jako średnia arytmetyczna bezwzględnej odelgłości początków i końców hipotez
	double dist(Hypo other) {
		double sd = start - other.start;
		double ed = (start + len) - (other.start + other.len);
		return (fabs(sd) + fabs(ed)) / 2.0;
	}
};

/**
 * Metoda do porównywania węzłów (arcs) kraty z wybranym wyrazem.
 * Funkcja ta jest podawana do metody "get" w kracie.
 * Służy do przeszukiwania kraty w poszukiwaniu słów zawartych w stringu "str".
 * Funkcja ta zwraca true jeśli wyraz w węźle jest początkiem wyrazu w "str".
 * Inaczej mówiąc jeśli: str.startsWith(a->name)
 */
bool comp(Arc* a, void* arg);

/**
 * Rekurencyjna metoda do przeszukiwania wszsystkich węzłów w kracie w poszukiwaniu prawidłowych hipotez.
 * Jako argument dostaje bieżącą hipotezę i listę węzłów do sprawdzenia.
 * Argumenty "lat" i "str" się nie zmieniają w kolejnych rekurencjach funkcji.
 * Dla każdego węzła w "arc", przedłuża hipotezę "h" o informacje zawarte w węźle i powtarza rekurencje dla jego następników.
 * Przed rekurencją sprawdza czy wyraz jest kompletny, albo czy już nie pasuje do "str" i tam kończy rekurencję.
 */
vector<Hypo> rec(Lattice *lat, Hypo h, vector<Arc*> arc, Trans trans);

/**
 * Czyści listę hipotez na podstawie odległości policzonej z metody Hypo::dist.
 * Chodzi o to żeby usunąć  hipotezy, które są blisko siebie i zostawić tylko najlepszą.
 */
vector<Hypo> prune(vector<Hypo> hypo, double threshold);

/**
 * Leksykon - niestety musi być globalny.
 */
Lexicon lex;

int main(int argc, char** argv) {

	if (argc == 3) {
		Lattice lat;

		if (!lat.load(argv[1])) {
			cout << "Error reading lattice!" << endl;
			return 0;
		}

		lat.save_wordlist(argv[2]);
		return 0;
	}

	if (argc != 4 && argc != 5) {
		cout << argv[0] << " [lattice] [wordlist_out]" << endl;
		cout << argv[0] << " [lattice] [keywords] [lexicon]" << endl;
		cout << argv[0] << " [lattice] [keywords] [lexicon] -d" << endl;
		return 0;
	}

	bool debug = false;
	if (argc == 5 && string(argv[4]) == "-d") {
		debug = true;
	}

	Lattice lat;

	if (!lat.load(argv[1])) {
		cout << "Error reading lattice!" << endl;
		return 0;
	}

	if (!lex.load(argv[3])) {
		cout << "Error loading lexicon!" << endl;
		return 0;
	}

	ifstream kwfile(argv[2]);
	if (kwfile.fail()) {
		cout << "Cannot open keyword file!" << endl;
		return 0;
	}

	while (true) {

		string keyword;

		getline(kwfile, keyword);

		if (kwfile.fail())
			break;

		Trans trans = lex.get(keyword);

		if (trans.empty()) {
			cout << "Keyword missing in lexicon: " << keyword << endl;
			continue;
		}

		//pobierz wszystkie węzły, które rozpoczynają wyraz "mauritius"
		//np. "mau+", "ma", "ma+", itd.
		vector<Arc*> ret = lat.get(comp, &trans);

		//posortuj listę węzłów i usuń zbędne (na podstawie warunku viterbiego)
		//jest też opcjonalny argument, który zostawia tylko N najlepszych
		//na razie polecam nie używać tego argumentu (zwracać wszystko), chyba że będą powody (zbyt długie obliczenia)
		ret = nbest(ret);

		//na podstawie powyższej listy, rekurencyjnie poszukaj resztę wyrazów
		vector<Hypo> hyps = rec(&lat, Hypo(), ret, trans);

		//posortuj i wyczyść wynik
		sort(hyps.begin(), hyps.end());
		hyps = prune(hyps, 10);

		//wypisz na ekran
		for (size_t i = 0; i < hyps.size(); i++) {
			cout << keyword << " " << hyps[i].start / 100.0 << " "
					<< hyps[i].len / 100.0 << " " << hyps[i].w << endl;
			if (debug) {
				cout << hyps[i].word << endl;
				for (size_t j = 0; j < hyps[i].trans.phones.size(); j++) {
					cout << hyps[i].trans.phones[j].toSampa() << endl;
				}
			}
		}
	}

	kwfile.close();

	return 0;
}

bool comp(Arc* a, void* arg) {

	Trans* kw = (Trans*) arg;
	string name = a->name;
	Trans t = lex.get(name);

	/*if (name == "mau+") {
	 for (size_t j = 0; j < kw->phones.size(); j++)
	 cout << "KW " << kw->phones[j].toSampa() << endl;
	 for (size_t j = 0; j < t.phones.size(); j++)
	 cout << "T " << t.phones[j].toSampa() << endl;
	 }*/

	return kw->startsWith(t);
}

vector<Hypo> rec(Lattice *lat, Hypo h, vector<Arc*> arc, Trans trans) {

	vector<Hypo> hypos;
	vector<Arc*>::iterator beg, end;

	for (beg = arc.begin(), end = arc.end(); beg != end; beg++) {

		Hypo hn;
		Trans tn;

		Arc* a = *beg;

		Trans t = lex.get(a->name);

		if (h.trans.empty())
			tn = t;
		else
			tn = h.trans.appendFilter(t, trans);

		if (tn.empty())
			continue;

		hn.trans = tn;
		if (h.word.empty())
			hn.word = a->name;
		else
			hn.word = h.word + " " + a->name;

		if (h.start < 0)
			hn.start = a->state_off;
		else
			hn.start = h.start;
		hn.len = h.len + a->state_len;
		hn.w = h.w + a->w_a + a->w_b;

		if (hn.trans.equals(trans))
			hypos.push_back(hn);
		else {
			vector<Arc*> ret = lat->get(a->end);
			vector<Hypo> hypos_ret = rec(lat, hn, ret, trans);
			hypos.insert(hypos.end(), hypos_ret.begin(), hypos_ret.end());
		}

	}
	return hypos;
}

vector<Hypo> prune(vector<Hypo> hypo, double threshold) {

	list<Hypo> lhyps;
	copy(hypo.begin(), hypo.end(), back_inserter(lhyps));
	hypo.clear();

	while (!lhyps.empty()) {
		Hypo h = lhyps.front();
		lhyps.pop_front();
		hypo.push_back(h);
		list<Hypo>::iterator beg = lhyps.begin();
		list<Hypo>::iterator end = lhyps.end();
		while (beg != end) {
			if (h.dist(*beg) < threshold)
				beg = lhyps.erase(beg);
			else
				beg++;
		}

	}
	return hypo;
}
