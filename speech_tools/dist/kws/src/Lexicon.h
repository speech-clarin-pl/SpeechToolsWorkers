/*
 * lexicon.h
 *
 *  Created on: Nov 12, 2015
 *      Author: guest
 */

#ifndef LEXICON_H_
#define LEXICON_H_

#include <map>
#include <vector>
#include <string>

using std::map;
using std::vector;
using std::string;

class Phword {
private:
	vector<char> codes;

public:
	Phword();
	Phword(string sampa);

	string toSampa();

	bool equals(Phword);
	bool startsWith(Phword);

	Phword append(Phword phword);
};

class Trans {
public:
	vector<Phword> phones;

	Trans() {
	}

	Trans appendFilter(Trans a, Trans f);

	bool startsWith(Trans t);
	bool equals(Trans t);

	bool empty();
};

class Lexicon {

private:
	map<string, Trans> trans;

public:

	void add(string word, string sampa);

	bool load(string filename);
	bool save(string filename);

	Trans get(string word);
};

#endif /* LEXICON_H_ */
