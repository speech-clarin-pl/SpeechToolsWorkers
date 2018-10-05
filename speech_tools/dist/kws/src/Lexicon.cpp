/*
 * lexicon.cpp
 *
 *  Created on: Nov 12, 2015
 *      Author: guest
 */

#include "Lexicon.h"
#include <sstream>
#include <fstream>

using namespace std;

map<string, char> s2c;
string c2s[37];

bool initialized = false;

void initMaps() {
	if (!initialized) {
		initialized = true;

		c2s[0] = "i";
		c2s[1] = "I";
		c2s[2] = "e";
		c2s[3] = "a";
		c2s[4] = "o";
		c2s[5] = "u";
		c2s[6] = "en";
		c2s[7] = "on";
		c2s[8] = "p";
		c2s[9] = "b";
		c2s[10] = "t";
		c2s[11] = "d";
		c2s[12] = "k";
		c2s[13] = "g";
		c2s[14] = "f";
		c2s[15] = "v";
		c2s[16] = "s";
		c2s[17] = "z";
		c2s[18] = "S";
		c2s[19] = "Z";
		c2s[20] = "si";
		c2s[21] = "zi";
		c2s[22] = "x";
		c2s[23] = "ts";
		c2s[24] = "dz";
		c2s[25] = "tS";
		c2s[26] = "dZ";
		c2s[27] = "tsi";
		c2s[28] = "dzi";
		c2s[29] = "m";
		c2s[30] = "n";
		c2s[31] = "ni";
		c2s[32] = "N";
		c2s[33] = "l";
		c2s[34] = "r";
		c2s[35] = "w";
		c2s[36] = "j";

		s2c["i"] = 0;
		s2c["I"] = 1;
		s2c["e"] = 2;
		s2c["a"] = 3;
		s2c["o"] = 4;
		s2c["u"] = 5;
		s2c["en"] = 6;
		s2c["on"] = 7;
		s2c["p"] = 8;
		s2c["b"] = 9;
		s2c["t"] = 10;
		s2c["d"] = 11;
		s2c["k"] = 12;
		s2c["g"] = 13;
		s2c["f"] = 14;
		s2c["v"] = 15;
		s2c["s"] = 16;
		s2c["z"] = 17;
		s2c["S"] = 18;
		s2c["Z"] = 19;
		s2c["si"] = 20;
		s2c["zi"] = 21;
		s2c["x"] = 22;
		s2c["ts"] = 23;
		s2c["dz"] = 24;
		s2c["tS"] = 25;
		s2c["dZ"] = 26;
		s2c["tsi"] = 27;
		s2c["dzi"] = 28;
		s2c["m"] = 29;
		s2c["n"] = 30;
		s2c["ni"] = 31;
		s2c["N"] = 32;
		s2c["l"] = 33;
		s2c["r"] = 34;
		s2c["w"] = 35;
		s2c["j"] = 36;
	}
}

char get_s2c(string s) {
	if (s2c.find(s) != s2c.end()) {
		return s2c[s];
	}
	return -1;
}

string get_c2s(char c) {
	if (c < 0 || c >= 37)
		return "";
	else
		return c2s[(int) c];
}

Phword::Phword() {
}

Phword::Phword(string sampa) {
	initMaps();

	stringstream sstr(sampa);
	string ph;
	while (true) {
		sstr >> ph;
		if (sstr.fail())
			break;
		codes.push_back(get_s2c(ph));
	}
}

string Phword::toSampa() {
	if (codes.empty())
		return "";

	string ret = get_c2s(codes[0]);
	for (size_t i = 1; i < codes.size(); i++)
		ret += " " + get_c2s(codes[i]);
	return ret;
}

bool Phword::equals(Phword w) {

	if (codes.size() != w.codes.size())
		return false;

	for (size_t i = 0; i < codes.size(); i++)
		if (codes[i] != w.codes[i])
			return false;

	return true;
}

bool Phword::startsWith(Phword w) {

	if (codes.size() < w.codes.size())
		return false;

	for (size_t i = 0; i < w.codes.size(); i++)
		if (codes[i] != w.codes[i])
			return false;

	return true;

}

Phword Phword::append(Phword w) {
	Phword ret;
	for (size_t i = 0; i < codes.size(); i++)
		ret.codes.push_back(codes[i]);
	for (size_t i = 0; i < w.codes.size(); i++)
		ret.codes.push_back(w.codes[i]);
	return ret;
}

bool Trans::startsWith(Trans t) {
	vector<Phword>::iterator b1, e1, b2, e2;
	for (b1 = phones.begin(), e1 = phones.end(); b1 != e1; b1++)
		for (b2 = t.phones.begin(), e2 = t.phones.end(); b2 != e2; b2++)
			if ((*b1).startsWith(*b2))
				return true;
	return false;
}

bool Trans::equals(Trans t) {
	vector<Phword>::iterator b1, e1, b2, e2;
	for (b1 = phones.begin(), e1 = phones.end(); b1 != e1; b1++)
		for (b2 = t.phones.begin(), e2 = t.phones.end(); b2 != e2; b2++)
			if ((*b1).equals(*b2))
				return true;
	return false;
}

bool Trans::empty() {
	return phones.empty();
}

Trans Trans::appendFilter(Trans a, Trans f) {
	Trans ret;
	vector<Phword>::iterator b1, e1, b2, e2, b3, e3;
	for (b1 = phones.begin(), e1 = phones.end(); b1 != e1; b1++)
		for (b2 = a.phones.begin(), e2 = a.phones.end(); b2 != e2; b2++) {
			Phword w = (*b1).append(*b2);

			bool b = false;
			for (b3 = f.phones.begin(), e3 = f.phones.end(); b3 != e3; b3++) {
				if ((*b3).startsWith(w)) {
					b = true;
					break;
				}
			}

			if (b)
				ret.phones.push_back(w);
		}
	return ret;
}

void Lexicon::add(string word, string sampa) {

	trans[word].phones.push_back(Phword(sampa));
}

bool Lexicon::load(string filename) {
	ifstream file(filename.c_str());

	if (file.fail())
		return false;

	string line, word, sampa;
	size_t p;
	bool ret = true;
	while (true) {
		getline(file, line);
		if (file.fail())
			break;

		p = line.find_first_of(' ');
		if (p == string::npos) {
			ret = false;
			break;
		}

		word = line.substr(0, p);
		sampa = line.substr(p + 1);

		trans[word].phones.push_back(Phword(sampa));
	}

	file.close();
	return ret;
}

bool Lexicon::save(string filename) {

	ofstream file(filename.c_str());
	if (file.fail())
		return false;

	map<string, Trans>::iterator beg, end;
	string word;
	Trans t;
	for (beg = trans.begin(), end = trans.end(); beg != end; beg++) {
		word = (*beg).first;
		t = (*beg).second;
		for (size_t i = 0; i < t.phones.size(); i++)
			file << word << " " << t.phones[i].toSampa() << endl;
	}

	file.close();

	return true;
}

Trans Lexicon::get(string word) {

	return trans[word];

}
