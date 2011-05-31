cpp_keywords = \
    "asm auto bool break case catch char class const const_cast continue "\
    "default delete do double dynamic_cast else enum explicit export extern false float for "\
    "friend goto if inline int long mutable namespace new operator private protected public "\
    "register reinterpret_cast return short signed sizeof static static_cast struct switch "\
    "template this throw true try typedef typeid typename union unsigned using "\
    "virtual void volatile wchar_t while"

doxygen_keywords = \
    "a addindex addtogroup anchor arg attention "\
    "author b brief bug c class code date def defgroup deprecated dontinclude "\
    "e em endcode endhtmlonly endif endlatexonly endlink endverbatim enum example exception "\
    "f$ f[ f] file fn hideinitializer htmlinclude htmlonly "\
    "if image include ingroup internal invariant interface latexonly li line link "\
    "mainpage name namespace nosubgrouping note overload "\
    "p page par param post pre ref relates remarks return retval "\
    "sa section see showinitializer since skip skipline struct subsection "\
    "test throw todo typedef union until "\
    "var verbatim verbinclude version warning weakgroup $ @ \ & < > # { }"


java_keywords = \
    "abstract assert boolean break byte case catch char class "\
    "const continue default do double else extends final finally float for future "\
    "generic goto if implements import inner instanceof int interface long "\
    "native new null outer package private protected public rest "\
    "return short static super switch synchronized this throw throws "\
    "transient try var void volatile while"

javadoc_keywords = \
    "author code docRoot deprecated exception inheritDoc link linkplain "\
    "literal param return see serial serialData serialField since throws "\
    "value version"

perl_keywords = \
    "NULL __FILE__ __LINE__ __PACKAGE__ __DATA__ __END__ AUTOLOAD "\
    "BEGIN CORE DESTROY END EQ GE GT INIT LE LT NE CHECK abs accept "\
    "alarm and atan2 bind binmode bless caller chdir chmod chomp chop "\
    "chown chr chroot close closedir cmp connect continue cos crypt "\
    "dbmclose dbmopen defined delete die do dump each else elsif endgrent "\
    "endhostent endnetent endprotoent endpwent endservent eof eq eval "\
    "exec exists exit exp fcntl fileno flock for foreach fork format "\
    "formline ge getc getgrent getgrgid getgrnam gethostbyaddr gethostbyname "\
    "gethostent getlogin getnetbyaddr getnetbyname getnetent getpeername "\
    "getpgrp getppid getpriority getprotobyname getprotobynumber getprotoent "\
    "getpwent getpwnam getpwuid getservbyname getservbyport getservent "\
    "getsockname getsockopt glob gmtime goto grep gt hex if index "\
    "int ioctl join keys kill last lc lcfirst le length link listen "\
    "local localtime lock log lstat lt m map mkdir msgctl msgget msgrcv "\
    "msgsnd my ne next no not oct open opendir or ord our pack package "\
    "pipe pop pos print printf prototype push q qq qr quotemeta qu "\
    "qw qx rand read readdir readline readlink readpipe recv redo "\
    "ref rename require reset return reverse rewinddir rindex rmdir "\
    "s scalar seek seekdir select semctl semget semop send setgrent "\
    "sethostent setnetent setpgrp setpriority setprotoent setpwent "\
    "setservent setsockopt shift shmctl shmget shmread shmwrite shutdown "\
    "sin sleep socket socketpair sort splice split sprintf sqrt srand "\
    "stat study sub substr symlink syscall sysopen sysread sysseek "\
    "system syswrite tell telldir tie tied time times tr truncate "\
    "uc ucfirst umask undef unless unlink unpack unshift untie until "\
    "use utime values vec wait waitpid wantarray warn while write "\
    "x xor y"

python_keywords = \
    "and assert break class continue def del elif else except " \
    "exec finally for from global if import in is lambda None not or pass print " \
    "raise return try while yield"

ruby_keywords = \
    "__FILE__ and def end in or self unless __LINE__ begin "\
    "defined? ensure module redo super until BEGIN break do false next rescue "\
    "then when END case else for nil retry true while alias class elsif if "\
    "not return undef yield"

sql_keywords = \
    "ABSOLUTE ACTION ADD ADMIN AFTER AGGREGATE " \
    "ALIAS ALL ALLOCATE ALTER AND ANY ARE ARRAY AS ASC " \
    "ASSERTION AT AUTHORIZATION "\
    "BEFORE BEGIN BINARY BIT BLOB BOOLEAN BOTH BREADTH BY "\
    "CALL CASCADE CASCADED CASE CAST CATALOG CHAR CHARACTER "\
    "CHECK CLASS CLOB CLOSE COLLATE COLLATION COLUMN COMMIT "\
    "COMPLETION CONNECT CONNECTION CONSTRAINT CONSTRAINTS "\
    "CONSTRUCTOR CONTINUE CORRESPONDING CREATE CROSS CUBE CURRENT "\
    "CURRENT_DATE CURRENT_PATH CURRENT_ROLE CURRENT_TIME CURRENT_TIMESTAMP "\
    "CURRENT_USER CURSOR CYCLE "\
    "DATA DATE DAY DEALLOCATE DEC DECIMAL DECLARE DEFAULT "\
    "DEFERRABLE DEFERRED DELETE DEPTH DEREF DESC DESCRIBE DESCRIPTOR "\
    "DESTROY DESTRUCTOR DETERMINISTIC DICTIONARY DIAGNOSTICS DISCONNECT "\
    "DISTINCT DOMAIN DOUBLE DROP DYNAMIC "\
    "EACH ELSE END END-EXEC EQUALS ESCAPE EVERY EXCEPT "\
    "EXCEPTION EXEC EXECUTE EXTERNAL "\
    "FALSE FETCH FIRST FLOAT FOR FOREIGN FOUND FROM FREE FULL "\
    "FUNCTION "\
    "GENERAL GET GLOBAL GO GOTO GRANT GROUP GROUPING "\
    "HAVING HOST HOUR "\
    "IDENTITY IGNORE IMMEDIATE IN INDICATOR INITIALIZE INITIALLY "\
    "INNER INOUT INPUT INSERT INT INTEGER INTERSECT INTERVAL "\
    "INTO IS ISOLATION ITERATE "\
    "JOIN "\
    "KEY "\
    "LANGUAGE LARGE LAST LATERAL LEADING LEFT LESS LEVEL LIKE "\
    "LIMIT LOCAL LOCALTIME LOCALTIMESTAMP LOCATOR "\
    "MAP MATCH MINUTE MODIFIES MODIFY MODULE MONTH "\
    "NAMES NATIONAL NATURAL NCHAR NCLOB NEW NEXT NO NONE "\
    "NOT NULL NUMERIC "\
    "OBJECT OF OFF OLD ON ONLY OPEN OPERATION OPTION "\
    "OR ORDER ORDINALITY OUT OUTER OUTPUT "\
    "PAD PARAMETER PARAMETERS PARTIAL PATH POSTFIX PRECISION PREFIX "\
    "PREORDER PREPARE PRESERVE PRIMARY "\
    "PRIOR PRIVILEGES PROCEDURE PUBLIC "\
    "READ READS REAL RECURSIVE REF REFERENCES REFERENCING RELATIVE "\
    "RESTRICT RESULT RETURN RETURNS REVOKE RIGHT "\
    "ROLE ROLLBACK ROLLUP ROUTINE ROW ROWS "\
    "SAVEPOINT SCHEMA SCROLL SCOPE SEARCH SECOND SECTION SELECT "\
    "SEQUENCE SESSION SESSION_USER SET SETS SIZE SMALLINT SOME| SPACE "\
    "SPECIFIC SPECIFICTYPE SQL SQLEXCEPTION SQLSTATE SQLWARNING START "\
    "STATE STATEMENT STATIC STRUCTURE SYSTEM_USER "\
    "TABLE TEMPORARY TERMINATE THAN THEN TIME TIMESTAMP "\
    "TIMEZONE_HOUR TIMEZONE_MINUTE TO TRAILING TRANSACTION TRANSLATION "\
    "TREAT TRIGGER TRUE "\
    "UNDER UNION UNIQUE UNKNOWN "\
    "UNNEST UPDATE USAGE USER USING "\
    "VALUE VALUES VARCHAR VARIABLE VARYING VIEW "\
    "WHEN WHENEVER WHERE WITH WITHOUT WORK WRITE "\
    "YEAR "\
    "ZONE"

verilog_keywords =\
                 "always end endcase begin endfunction module "\
                 "case endmodule casex function or default if "\
                 "else initial and table rcmos task "\
                 "ifnone casez join release assign "\
                 "cmos large repeat deassign macromodule rnmos "\
                 "medium rpmos disable nand rtran edge nmos "\
                 "rtranif0 vectored endprimitive nor rtranif1 wait endspecify not scalared wand "\
                 "endtable endtask specify event pmos "\
                 "while for primitive wor force pull0 strong1 "\
                 "xnor forever xor fork "

verilog_keywords2 =\
                 "inout posedge input reg "\
                 "tri case negedge tri0 tri1 output "\
                 "wire  parameter highz0 pullup buf highz1 "\
                 "bufif0  real time bufif1 integer realtime tran tranif0 "\
                 "tranif1  triand defparam "\
                 "trior trireg "\
                 "notif0 small weak0 notif1  weak1  "\
                 "specparam  strong0 pull0 strong1 "\
                 "pull1 supply0 pulldown supply "

vxml_elements =\
    "assign audio block break catch choice clear disconnect else elseif "\
    "emphasis enumerate error exit field filled form goto grammar help "\
    "if initial link log menu meta noinput nomatch object option p paragraph "\
    "param phoneme prompt property prosody record reprompt return s say-as "\
    "script sentence subdialog submit throw transfer value var voice vxml"

vxml_attributes=\
    "accept age alphabet anchor application base beep bridge category charset "\
    "classid cond connecttimeout content contour count dest destexpr dtmf dtmfterm "\
    "duration enctype event eventexpr expr expritem fetchtimeout finalsilence "\
    "gender http-equiv id level maxage maxstale maxtime message messageexpr "\
    "method mime modal mode name namelist next nextitem ph pitch range rate "\
    "scope size sizeexpr skiplist slot src srcexpr sub time timeexpr timeout "\
    "transferaudio type value variant version volume xml:lang"

vxml_keywords = vxml_elements + " " + vxml_attributes + " " + "public !doctype"

hypertext_elements=\
    "a abbr acronym address applet area b base basefont " \
    "bdo big blockquote body br button caption center " \
    "cite code col colgroup dd del dfn dir div dl dt em " \
    "fieldset font form frame frameset h1 h2 h3 h4 h5 h6 " \
    "head hr html i iframe img input ins isindex kbd label " \
    "legend li link map menu meta noframes noscript " \
    "object ol optgroup option p param pre q s samp " \
    "script select small span strike strong style sub sup " \
    "table tbody td textarea tfoot th thead title tr tt u ul " \
    "var xml xmlns"

hypertext_attributes=\
    "abbr accept-charset accept accesskey action align alink " \
    "alt archive axis background bgcolor border " \
    "cellpadding cellspacing char charoff charset checked cite " \
    "class classid clear codebase codetype color cols colspan " \
    "compact content coords " \
    "data datafld dataformatas datapagesize datasrc datetime " \
    "declare defer dir disabled enctype event " \
    "face for frame frameborder " \
    "headers height href hreflang hspace http-equiv " \
    "id ismap label lang language leftmargin link longdesc " \
    "marginwidth marginheight maxlength media method multiple " \
    "name nohref noresize noshade nowrap " \
    "object onblur onchange onclick ondblclick onfocus " \
    "onkeydown onkeypress onkeyup onload onmousedown " \
    "onmousemove onmouseover onmouseout onmouseup " \
    "onreset onselect onsubmit onunload " \
    "profile prompt readonly rel rev rows rowspan rules " \
    "scheme scope selected shape size span src standby start style " \
    "summary tabindex target text title topmargin type usemap " \
    "valign value valuetype version vlink vspace width " \
    "text password checkbox radio submit reset " \
    "file hidden image"

hypertext_keywords = hypertext_elements + " " + hypertext_attributes + " " + "public !doctype"

php_keywords =\
    "and argv as argc break case cfunction class continue declare default do "\
    "die echo else elseif empty enddeclare endfor endforeach endif endswitch "\
    "endwhile E_ALL E_PARSE E_ERROR E_WARNING eval exit extends FALSE for "\
    "foreach function global HTTP_COOKIE_VARS HTTP_GET_VARS HTTP_POST_VARS "\
    "HTTP_POST_FILES HTTP_ENV_VARS HTTP_SERVER_VARS if include include_once "\
    "list new not NULL old_function or parent PHP_OS PHP_SELF PHP_VERSION "\
    "print require require_once return static switch stdClass this TRUE var "\
    "xor virtual while __FILE__ __LINE__ __sleep __wakeup"

sgml_keywords = "ELEMENT DOCTYPE ATTLIST ENTITY NOTATION"

yaml_keywords = "true false yes no"

xslt_elements = \
    "apply-templates call-template apply-imports for-each value-of copy-of "\
    "number choose if text copy variable message fallback "\
    "processing-instruction comment element attribute import include "\
    "strip-space preserve-space output key decimal-format attribute-set "\
    "variable param template namespace-alias stylesheet transform when "\
    "otherwise"

xslt_attributes = \
    "extension-element-prefixes exclude-result-prefixes id version "\
    "xmlns:xsl href elements method encoding omit-xml-declaration "\
    "standalone doctype-public doctype-system cdata-section-elements "\
    "indent media-type name match use name decimal-separator "\
    "grouping-separator infinity minus-sign NaN percent per-mille "\
    "zero-digit digit pattern-separator stylesheet-prefix "\
    "result-prefix match name priority mode select "\
    "disable-output-escaping level count from value format lang "\
    "letter-value grouping-separator grouping-size lang data-type "\
    "order case-order test use-attribute-sets " \
    "disable-output-escaping namespace terminate"\


xslt_keywords = xslt_elements + " " + xslt_attributes + " " + ' '.join(
        ['xsl:' + word for word in (xslt_elements + " " + xslt_attributes).split(' ')]
    )  

# XXX Fill these in!
js_keywords = ""
vb_keywords = ""  

css_keywords = \
    "font-family font-style font-variant font-weight font-size font " \
    "color background-color background-image background-repeat background-attachment background-position background " \
    "word-spacing letter-spacing text-decoration vertical-align text-transform text-align text-indent line-height " \
    "margin-top margin-right margin-bottom margin-left margin " \
    "padding-top padding-right padding-bottom padding-left padding " \
    "border-top-width border-right-width border-bottom-width border-left-width border-width " \
    "border-top border-right border-bottom border-left border " \
    "border-color border-style width height float clear " \
    "display white-space list-style-type list-style-image list-style-position list-style"

css_pseudo_classes = \
    "first-letter first-line link active visited "\
    "first-child focus hover lang before after left right first"

css_keywords_2 = "first-letter first-line active link visited"