#ifndef LATTICE_H_
#define LATTICE_H_

#include <string>
#include <vector>

using std::string;
using std::vector;

/**
 * Klasa reprezentująca jeden węzeł w kracie.
 * Właściwie reprezetowane są przejścia, ale możemy to nazywać węzłami.
 */
class Arc {
public:
	Arc() :
			id(0), start(0), end(0), name(""), w_a(0), w_b(0), state_len(0), state_off(
					0) {
	}

	Arc(int id, string line);

	int id; //pozycja w wektorze Lattice::arcs
	int start, end; //początkowy i końcowy stan przejścia, czyli to przejście biegnie od start -> end
	string name; //tekst (wyraz) wpisany w węźle
	double w_a, w_b; //wagi (pierwsza to waga grafu, a druga waga akustyczna)
	int state_len; //ilość przejść fonetycznych (okienek) na ten węzeł kraty
	int state_off; //odstęp ilości przejść od początku kraty (przeliczone podczas ładowania kraty)
	string toString(); //funkcja wypisująca opis węzła - dla debugu
};

/**
 * Klasa reprezentująca kratę
 */
class Lattice {
private:

	string name; //nazwa pliku (zapisana w pierwszej linii pliku)
	vector<Arc> arcs; //wszystkie węzły (przejścia) w kolejności jak występują w pliku
	int state_num; //ilość stanów (maksymalny indeks stanu używany przez węzły)
	int last_state; //ostatni stan (liczba w ostatniej linii pliku) -- nie jest w tej chwili do niczego potrzebne

	vector<Arc*> *state; //wskażniki do węzło posortowane według stanu początkowego

public:

	Lattice();
	~Lattice();

	//wczytuje kratę z pliku tekstowego
	bool load(string path);

	//zapisuje listę słów z kraty
	bool save_wordlist(string name);

	//zwraca wszystkie węzły zaczynające się od danego stanu
	vector<Arc*> get(int state);

	//zwraca wszystkie węzły dla których metoda comp(a,str) zwróci true
	vector<Arc*> get(bool (*comp)(Arc*, void*), void* arg);

};

//Sortuje listę węzłów według prawdopodobieństwa.
//Potem usuwa te węzły które mają taką samą nazwę i ten sam stan końcowy.
//Przy tym zostawiany jest jeden węzeł o najwyższym prawdopodobieńśtwie.
//Węzły o tej samej nazwie i stanie końcowym są równoważne w kracie i wystarczy nam jeden najlepszy.
//Dodatkowy parametr N kasuje wszystkie najgorsze węzły zostawiając tylko N najlepszych.
//Jeśli N jest <=0 albo >rozmiaru listy węzłów, zwracane są wszystkie węzły.
vector<Arc*> nbest(vector<Arc*> arcs, int n = 0); //0 - ALL

#endif /* LATTICE_H_ */
