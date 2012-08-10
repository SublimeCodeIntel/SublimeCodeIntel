/*  -*- tab-width: 8; indent-tabs-mode: t -*-
 * Scintilla source code edit control
 * @file LexTcl.cxx
 * Lexer for Tcl.
 */
// Copyright (c) 2001-2006 ActiveState Software Inc.
// The License.txt file describes the conditions under which this software may
// be distributed.

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <assert.h>
#include <ctype.h>

#include "ILexer.h"
#include "Scintilla.h"
#include "SciLexer.h"

#include "WordList.h"
#include "LexAccessor.h"
#include "Accessor.h"
#include "StyleContext.h"
#include "CharacterSet.h"
#include "LexerModule.h"

#ifdef SCI_NAMESPACE
using namespace Scintilla;
#endif

#if 1	// No Debug
#define colourString(end, state, styler) styler.ColourTo(end, state)
#else	// Debug color printfs
#define colourString(end, state, styler) \
	describeString(end, state, styler), styler.ColourTo(end, state)

static char *stateToString(int state) {
    switch (state) {
    case SCE_TCL_DEFAULT:	return "default";
    case SCE_TCL_NUMBER:	return "number";
    case SCE_TCL_WORD:		return "word";
    case SCE_TCL_COMMENT:	return "comment";
    case SCE_TCL_STRING:	return "string";
    case SCE_TCL_CHARACTER:	return "character";
    case SCE_TCL_LITERAL:	return "literal";
    case SCE_TCL_OPERATOR:	return "operator";
    case SCE_TCL_IDENTIFIER:	return "identifier";
    case SCE_TCL_EOL:		return "eol";
    case SCE_TCL_VARIABLE:	return "variable";
    case SCE_TCL_ARRAY:		return "array";
    default:			return "unknown";
    }
}

static void describeString(int end, int state, Accessor &styler) {
    char s[1024];
    int start = styler.GetStartSegment();
    int len = end - start + 1;

    if (!len) { return; }

    for (int i = 0; i < len && i < 100; i++) {
	s[i] = styler[start + i];
	s[i + 1] = '\0';
    }

    int start_line = styler.GetLine(start);
    int start_pos = start - styler.LineStart(start_line);
    int end_line = styler.GetLine(end);
    int end_pos = end - styler.LineStart(end_line);

    fprintf(stderr, "%s [%d] [(%d:%d)=>(%d:%d)]:\t'%s'\n",
	    stateToString(state), len,
	    start_line, start_pos,
	    end_line, end_pos,
	    s); fflush(stderr);
}
#endif

static inline bool isTclOperator(char ch) {
    // Fix bug 74850 -- the backslash acts as an operator outside strings
    // Otherwise other code processors won't see escaped things, esp. \{ and \}
    return strchr("(){}[];!%^&*-=+|<>?/\\", ch) != NULL;
}

static void classifyWordTcl(int start,
			    int end,
			    WordList &keywords,
			    Accessor &styler) {
    char s[100];
    char chAttr;
    bool wordIsNumber = isdigit(styler[start]) || (styler[start] == '.');

    for (int i = 0; i < end - start + 1 && i < 40; i++) {
	s[i] = styler[start + i];
	s[i + 1] = '\0';
    }

    if (wordIsNumber) {
	chAttr = SCE_TCL_NUMBER;
    } else if (keywords.InList(s)) {
	chAttr = SCE_TCL_WORD;
    } else {
	// was default, but that should be reserved for white-space,
	// and we had to see an alpha-char to get here
	chAttr = SCE_TCL_IDENTIFIER;
    }

    colourString(end, chAttr, styler);
}

// KOMODO  see if a style is one of our IO styles
static inline bool IsIOStyle(int style) {
	return style == SCE_TCL_STDIN ||
		style == SCE_TCL_STDOUT ||
		style == SCE_TCL_STDERR;
}

// By default there are 5 style bits, plenty for Tcl
#define STYLE_MASK 31
#define actual_style(style) (style & STYLE_MASK)

// Null transitions when we see we've reached the end
// and need to relex the curr char.

static void redo_char(int &i, char &ch, char &chNext, int &state) {
    i--;
    chNext = ch;
    state = SCE_TCL_DEFAULT;
}

static inline bool isSafeAlnum(char ch) {
    return ((unsigned int) ch >= 128) || isalnum(ch) || ch == '_';
}

static inline void advanceOneChar(int& i, char&ch, char& chNext, char chNext2) {
    i++;
    ch = chNext;
    chNext = chNext2;
}

#define BITSTATE_TOP_LEVEL  0x00
#define BITSTATE_IN_STRING  0x01
#define BITSTATE_IN_COMMAND 0x02
#define BITSTATE_IN_BRACE   0x03
#define BITSTATE_MASK       0x03
#define BITSTATE_MASK_SIZE  2

#define pushBitState(bitState, mask) bitState = ((bitState) << BITSTATE_MASK_SIZE) | (mask)

#define popBitState(bitState) bitState >>= BITSTATE_MASK_SIZE;

#define testBitStateNotTopLevel(bitState, mask) \
  (((bitState) & BITSTATE_MASK) == (mask))

static bool testBitStateOrTopLevel(unsigned int bitState,
				   unsigned int mask) {
    unsigned int part = bitState & BITSTATE_MASK;
    return !part || part == mask;
}

/**
 * We're in a situation like { ... " ...
 * Look at the line to the right of the '"'.  If it contains a
 * closing close-brace before we hit a '"' or eol or eof, return true
 *
 * The caller can then color the '"' as a tcl_literal.
 */
static bool lineContainsClosingBrace(int pos,
				     int lengthDoc,
				     Accessor &styler) {
    char ch;
    int numBraces = 0;
    for (; pos < lengthDoc; pos++) {
	ch = styler.SafeGetCharAt(pos);
	if (ch == '\\') {
	    pos++;
	} else if (ch == '"') {
	    return false;
	} else if (ch == '\n') {
	    return false;
	} else if (ch == '{') {
	    numBraces++;
	} else if (ch == '}') {
	    numBraces--;
	    if (numBraces < 0) {
		return true;
	    }
	}
    }
    return false;
}

static bool continuesComment(int pos,
			     Accessor &styler) {
    int style;
    styler.Flush();
    for (; pos >= 0; --pos) {
	style = actual_style(styler.StyleAt(pos));
	if (style == SCE_TCL_COMMENT) {
	    return true;
	} else if (style != SCE_TCL_DEFAULT) {
	    return false;
	}
    }
    return false;
}

static void ColouriseTclDoc(unsigned int startPos_,
			    int length,
			    int initStyle,
			    WordList *keywordlists[],
			    Accessor &styler) {
    WordList &keywords = *keywordlists[0];

    long bitState = 0;
    int startPos = (int) startPos_; // avoid unsigned int due to
                                    // bdry conditions at buffer start

    int inEscape	= 0;
    int inStrBraceCnt	= 0;
    // inCmtBraceCnt -- keeps track of the brace count in a block of
    // comments.  End it when we hit a different state.
    // This means that the synchronization always starts at a block of
    // comments as well.
    int inCmtBraceCnt   = 0;
    int lastQuoteSpot   = -1;
    // We're not always sure of the command start, but make an attempt
    bool cmdStart	= true;
    // Keep track of whether a variable is using braces or it is an array
    bool varBraced	= 0;

    //fprintf(stderr, "Start lexing at pos %d, len %d, style %d\n", startPos, length, initStyle);
    
    int state;
    int lengthDoc = startPos + length;
    if (IsIOStyle(initStyle)) {
	// KOMODO
	// Skip initial IO Style?
	while (startPos < lengthDoc
	       && IsIOStyle(actual_style(styler.StyleAt(startPos)))) {
	    startPos++;
	}
    } else {
	int start_line, style, start_line_pos = 0, pos;
	char ch;
	for (start_line = styler.GetLine(startPos);
	     start_line > 0;
	     --start_line) {
	    // Don't stop after an escaped line.
	    start_line_pos = styler.LineStart(start_line);
	    pos = start_line_pos - 1;
	    ch = styler.SafeGetCharAt(pos);
	    if (pos > 0 && ch == '\n') {
		pos -= 1;
		ch = styler.SafeGetCharAt(pos);
	    }
	    if (pos > 0 && ch == '\r') {
		pos -= 1;
		ch = styler.SafeGetCharAt(pos);
	    }
	    if (ch == '\\'
		|| actual_style(styler.StyleAt(pos)) == SCE_TCL_COMMENT) {
		continue;
	    }
	    bitState = styler.GetLineState(start_line - 1);
	    if (!testBitStateNotTopLevel(bitState, BITSTATE_IN_STRING)) {
		// Simplify: don't start in a multi-line string
		break;
	    }
	}
	lengthDoc = startPos + length + (start_line_pos - startPos);
	startPos = start_line_pos;
    }
    state = SCE_TCL_DEFAULT;
    //fprintf(stderr, "After sync, start at pos %d, len %d, style %d\n", startPos, length, initStyle);
    char chPrev		= ' ';
    char chNext		= styler[startPos];

    // Folding info
    int visibleChars = 0;
    int lineCurrent = styler.GetLine(startPos);
    int levelPrev   = styler.LevelAt(lineCurrent) & SC_FOLDLEVELNUMBERMASK;
    int levelMinPrev   = levelPrev;
    int levelCurrent = levelPrev;
    bool foldCompact = styler.GetPropertyInt("fold.compact", 1) != 0;
    bool foldAtElse = styler.GetPropertyInt("fold.at.else", 1) != 0;

    styler.StartAt(startPos);
    styler.StartSegment(startPos);
    for (int i = startPos; i < lengthDoc; i++) {
	char ch = chNext;
	chNext = styler.SafeGetCharAt(i + 1);

	if (styler.IsLeadByte(ch)) {
	    chNext = styler.SafeGetCharAt(i + 2);
	    chPrev = ' ';
	    i += 1;
	    visibleChars++;
	    cmdStart = false;
	    continue;
	}

	if (chPrev == '\\') {
	    // If the prev char was the escape char, flip the inEscape bit.
	    // This works because colorization always starts at the
	    // beginning of the line.
	    inEscape = !inEscape;
	} else if (inEscape) {
	    if (chPrev == '\r' && ch == '\n') {
		// Keep inEscape for one more round
	    } else {
		// Otherwise we aren't in an escape sequence
		inEscape = 0;
	    }
	}

	if ((ch == '\r' && chNext != '\n') || (ch == '\n')) {
	    // Trigger on CR only (Mac style) or either on LF from CR+LF
	    // (Dos/Win) or on LF alone (Unix) Avoid triggering two times on
	    // Dos/Win End of line
	    styler.SetLineState(lineCurrent, bitState);
	    if (state == SCE_TCL_EOL) {
		colourString(i, state, styler);
		state = SCE_TCL_DEFAULT;
	    }
#if 0
	    fprintf(stderr, "end of line %d, levelPrev=0x%0x, levelCurrent=0x%0x\n",
		    lineCurrent, levelPrev, levelCurrent);
#endif
	    int levelUse = foldAtElse ? levelMinPrev : levelPrev;
	    int lev = levelUse;
	    if (lev < SC_FOLDLEVELBASE) {
		lev = SC_FOLDLEVELBASE;
	    }
	    if (visibleChars == 0 && foldCompact) {
		lev |= SC_FOLDLEVELWHITEFLAG;
	    }
	    if ((levelCurrent > levelUse) && (visibleChars > 0)) {
		lev |= SC_FOLDLEVELHEADERFLAG;
	    }
	    if (lev != styler.LevelAt(lineCurrent)) {
		styler.SetLevel(lineCurrent, lev);
	    }
	    lineCurrent++;
	    levelMinPrev = levelPrev = levelCurrent;
	    visibleChars = 0;
	    if (state == SCE_TCL_DEFAULT && !inEscape) {
		cmdStart = true;
	    }
	} else if (!isspacechar(ch)) {
	    visibleChars++;
	}

	if (state == SCE_TCL_DEFAULT) {
	    if ((ch == '#') && cmdStart) {
		colourString(i-1, state, styler);
		state = SCE_TCL_COMMENT;
		if (i > 0 && !continuesComment(i - 1, styler)) {
		    inCmtBraceCnt = 0;
		}
		cmdStart = false;
	    } else if ((ch == '\"') && !inEscape) {
		if (testBitStateNotTopLevel(bitState, BITSTATE_IN_BRACE)) {
		    if (lineContainsClosingBrace(i + 1, lengthDoc, styler)) {
			// Do nothing, treat it like a literal.
			colourString(i-1, state, styler);
			colourString(i, SCE_TCL_LITERAL, styler);
		    } else {
			colourString(i-1, state, styler);
			state = SCE_TCL_STRING;
			pushBitState(bitState, BITSTATE_IN_STRING);
			inStrBraceCnt = 0;
			// Count braces in this string
			// Note that this brace-count doesn't survive
			// when a string is broken by a command.
		    }
		} else {
		    colourString(i-1, state, styler);
		    state = SCE_TCL_STRING;
		    pushBitState(bitState, BITSTATE_IN_STRING);
		    // Ignore braces in this string
		    inStrBraceCnt = -1;
		}
		cmdStart = false;
	    } else if (ch == '$') {
		colourString(i-1, state, styler);
		if (chNext == '{') {
		    varBraced = true;
		    advanceOneChar(i, ch, chNext, styler.SafeGetCharAt(i + 1));
		    state = SCE_TCL_VARIABLE;
		} else if (iswordchar(chNext)) {
		    varBraced = false;
		    state = SCE_TCL_VARIABLE;
		} else {
		    colourString(i, SCE_TCL_OPERATOR, styler);
		    // Stay in default mode.
		}
		cmdStart = false;
	    } else if (isTclOperator(ch) || ch == ':') {
		if (ch == '-' && isascii(chNext) && isalpha(chNext)) {
		    colourString(i-1, state, styler);
		    // We could call it an identifier, but then we'd need another
		    // state.  classifyWordTcl will do the right thing.
		    state = SCE_TCL_WORD;
		    cmdStart = false;
		} else {
		    // color up this one character as our operator
		    // multi-character operators will have their second
		    // character colored on the next pass
		    colourString(i-1, state, styler);
		    colourString(i, SCE_TCL_OPERATOR, styler);
		    if (!inEscape) {
			if (ch == '{' || ch == '[') {
			    if (ch == '{') {
				if (levelMinPrev > levelCurrent) {
				    levelMinPrev = levelCurrent;
				}
				pushBitState(bitState, BITSTATE_IN_BRACE);
			    } else {
				pushBitState(bitState, BITSTATE_IN_COMMAND);
			    }
			    ++levelCurrent;
			    cmdStart = true;
			} else if (ch == ']' || ch == '}') {
			    if ((levelCurrent & SC_FOLDLEVELNUMBERMASK) > SC_FOLDLEVELBASE) {
				--levelCurrent;
			    }
			    if (ch == ']') {
				if (testBitStateNotTopLevel(bitState, BITSTATE_IN_COMMAND)) {
				    popBitState(bitState);
				    if (testBitStateNotTopLevel(bitState, BITSTATE_IN_STRING)) {
					state = SCE_TCL_STRING;
				    }
				}
			    } else if (testBitStateNotTopLevel(bitState, BITSTATE_IN_BRACE)) {
				popBitState(bitState);
			    }
			} else if (ch == ';' && testBitStateOrTopLevel(bitState, BITSTATE_IN_BRACE)) {
			    cmdStart = true;
			}
		    }
		}
	    } else if (iswordstart(ch)) {
		colourString(i-1, state, styler);
		if (iswordchar(chNext)) {
		    state = SCE_TCL_WORD;
		} else {
		    classifyWordTcl(styler.GetStartSegment(), i,
				    keywords, styler);
		    // Stay in the default state
		}
		cmdStart = false;
	    } else if (!isspacechar(ch)) {
		cmdStart = false;
	    }
	} else if (state == SCE_TCL_WORD) {
	    if (!iswordchar(chNext)) {
		classifyWordTcl(styler.GetStartSegment(), i,
				keywords, styler);
		state = SCE_TCL_DEFAULT;
	    }
	} else {
	    if (state == SCE_TCL_VARIABLE) {
		/*
		 * A variable is ${?\w*}? and may be directly followed by
		 * another variable.  This should handle weird cases like:
		 * $a$b           ;# multiple vars
		 * ${a(def)(def)} ;# all one var
		 * ${abc}(def)    ;# (def) is not part of the var name now
		 * Previous to Komodo 4.2.1:
		 * $a(def)(ghi)   ;# (def) is array key, (ghi) is just chars
		 * ${a...}(def)(ghi)   ;# ( and ) are operators, def and ghi are chars
		 */
		if (!iswordchar(chNext)) {
		    bool varEndsHere = false;
		    if (varBraced) {
			if (chNext == '}') {
			    varBraced = false;
			    colourString(i + 1, state, styler);
			    state = SCE_TCL_DEFAULT;
			    advanceOneChar(i, ch, chNext, styler.SafeGetCharAt(i + 2));
			}
			// else continue building a var-braced string
		    } else if (chNext == ':' && styler.SafeGetCharAt(i + 2) == ':') {
			// continue, it's part of a simple name, but advance
			// so we don't stumble on the second colon
			advanceOneChar(i, ch, chNext, ':');
		    } else {
			varEndsHere = true;
		    }
		    if (varEndsHere) {
			colourString(i, state, styler);
			state = SCE_TCL_DEFAULT;
		    }
		}
	    } else if (state == SCE_TCL_COMMENT) {
		/*
		 * The line continuation character also works for comments.
		 */
		if ((ch == '\r' || ch == '\n') && !inEscape) {
		    colourString(i-1, state, styler);
		    state = SCE_TCL_DEFAULT;
		    cmdStart = true;
		} else if ((ch == '{') && !inEscape) {
		    inCmtBraceCnt++;
		} else if ((ch == '}') && !inEscape) {
		    inCmtBraceCnt--;
		    // Ignore braces at the top-level
		    // If we're processing a comment, the current bit-state
		    // is either clear or IN_BRACE
		    // Don't worry about 
		    if (inCmtBraceCnt == -1 && testBitStateNotTopLevel(bitState,
								       BITSTATE_IN_BRACE)) {
			popBitState(bitState);
			colourString(i - 1, state, styler);
			colourString(i, SCE_TCL_OPERATOR, styler);
			state = SCE_TCL_DEFAULT;
		    }
		}
	    } else if (state == SCE_TCL_STRING && !inEscape) {
		if (ch == '\r' || ch == '\n') {
		    /*
		     * In the case of EOL in a string where the line
		     * continuations character isn't used, leave us in the
		     * SCE_TCL_STRING state, but color the newline.
		     */
		    // No I think this is wrong -- EP
		    // The lexer will color it as a string if it hits
		    // a quote or EOF, otherwise it'll hit the brace
		    // and whip back.
		    
		    //!! colourString(i-1, state, styler);
		    //colourString(i, SCE_TCL_EOL, styler);
		    /*
		     * We are in a string, but in Tcl you can never really
		     * say when a command starts or not until eval.
		     */
		    cmdStart = true;
		} else if (ch == '\"') {
		    colourString(i, state, styler);
		    popBitState(bitState);
		    // We always pop to a default state
		    state = SCE_TCL_DEFAULT;
		} else if (ch == '[') {
		    pushBitState(bitState, BITSTATE_IN_COMMAND);
		    colourString(i, state, styler);
		    state = SCE_TCL_DEFAULT;
		    ++levelCurrent;
		    cmdStart = true;
		} else if (ch == '{') {
		    inStrBraceCnt++;
		} else if (ch == '}') {
		    inStrBraceCnt--;
		    if (inStrBraceCnt < 0) {
			// End the string here.
			colourString(i - 1, state, styler);
			popBitState(bitState);
			colourString(i - 1, SCE_TCL_OPERATOR, styler);
			state = SCE_TCL_DEFAULT;
			--levelCurrent;
		    }
		}
	    }
	}
	chPrev = ch;
    }
    // Make sure to colorize last part of document
    // If it was SCE_TCL_WORD (the default if we were in a word), then
    // check to see whether it's a legitamite word.
    if (state == SCE_TCL_WORD) {
	classifyWordTcl(styler.GetStartSegment(), lengthDoc - 1,
			keywords, styler);
    } else {
	colourString(lengthDoc - 1, state, styler);
    }
    int flagsNext = styler.LevelAt(lineCurrent) & ~SC_FOLDLEVELNUMBERMASK;
    styler.SetLevel(lineCurrent, levelPrev | flagsNext);
    styler.Flush();
}

static const char * const tclWordListDesc[] = {
    "Tcl keywords",
    0
};

LexerModule lmTcl(SCLEX_TCL, ColouriseTclDoc, "tcl", NULL,
		  tclWordListDesc);
