#include<fstream>    
#include<iostream> 

#include <./Simple>

using namespace std;

int 
main(int argc, char** argv) 
{        
    // we want to have error outputs in stdout, so that the unit test could see it.
    quex::Token   token;
    quex::Simple  qlex(argc == 1 ? "example.txt" : argv[1]);

    cout << "## An Assert-Abortion might be an intended element of the experiment.\n";
    qlex.token_p_set(&token);
    do {
        qlex.receive();
        cout << string(token) << endl;
    } while( token.type_id() != QUEX_TKN_TERMINATION );

    return 0;
}
