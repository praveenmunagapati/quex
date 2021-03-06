/* vim: set filetype=cpp:  -*- C++ -*-
 *
 * Declaration of all converter functions towards 'utf8', 'utf16', 'utf32',
 * 'char', and 'wchar_t': 
 *
 *    QUEX_CONVERTER_CHAR_DEF(cp866, utf8)(...)
 *    QUEX_CONVERTER_CHAR_DEF(cp866, utf16)(...)
 *    QUEX_CONVERTER_CHAR_DEF(cp866, utf32)(...)
 *    QUEX_CONVERTER_CHAR_DEF(cp866, char)(...)
 *    QUEX_CONVERTER_CHAR_DEF(cp866, wchar_t)(...)
 *
 *    QUEX_CONVERTER_STRING_DEF(cp866, utf8)(...)     for string and buffer 
 *    QUEX_CONVERTER_STRING_DEF(cp866, utf16)(...)    for string and buffer 
 *    QUEX_CONVERTER_STRING_DEF(cp866, utf32)(...)    for string and buffer 
 *    QUEX_CONVERTER_STRING_DEF(cp866, char)(...)     for string and buffer 
 *    QUEX_CONVERTER_STRING_DEF(cp866, wchar_t)(...)  for string and buffer 
 *
 * The declarations are generated by the file:
 *
 *             ../generator/declarations.g
 *
 * These functions ARE DEPENDENT on QUEX_TYPE_CHARACTER.
 * => Thus, they are placed in the analyzer's namespace.
 *
 * (C) 2012 Frank-Rene Schaefer. 
 *     ABSOLUTELY NO WARRANTY                                                */
/* 2010 (C) Frank-Rene Schaefer; ABSOLUTELY NO WARRANTY */
#if    ! defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866__) \
    ||   defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__TMP_DISABLED)
#if    ! defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__TMP_DISABLED)
#        define  __QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866__
#endif

#include <quex/code_base/converter_helper/common.h>

QUEX_NAMESPACE_MAIN_OPEN

#define __QUEX_FROM                cp866
#define __QUEX_FROM_TYPE           QUEX_TYPE_CHARACTER

#include <quex/code_base/converter_helper/generator/declarations.g>

QUEX_NAMESPACE_MAIN_CLOSE

#endif /* __QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866__                */

/* -*- C++ -*- vim: set syntax=cpp:
 * PURPOSE: 
 *
 * Provide the implementation of character and string converter functions
 * FROM the buffer's cp866 to utf8, utf16, utf32, char, and wchar_t.
 *
 * STEPS:
 *
 * (1) Implement the character converters from buffer's cp866 to 
 *     utf8, utf16, utf32. Those come out of quex's code generator.
 *
 * (1b) Derive the converts from cp866 to char and wchar_t from
 *      those converters. For this use:
 *
 *          "../generator/character-converter-char-wchar_t.gi"
 *
 * (2) Generate the implementation of the string converters in terms
 *     of those character converters.
 *
 *     Use: "../generator/implementation-string-converters.gi"
 *
 *          which uses
 *
 *              "../generator/string-converter.gi"
 *
 *          to implement each string converter from the given 
 *          character converters. 
 *
 * These functions ARE DEPENDENT on QUEX_TYPE_CHARACTER.
 * => Thus, they are placed in the analyzer's namespace.
 *
 * 2010 (C) Frank-Rene Schaefer; 
 * ABSOLUTELY NO WARRANTY                                                    */
#if    ! defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866_I) \
    ||   defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__TMP_DISABLED)
#if    ! defined(__QUEX_INCLUDE_GUARD__CONVERTER_HELPER__TMP_DISABLED)
#        define  __QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866_I
#endif

#include "converter-tester.h"

QUEX_NAMESPACE_MAIN_OPEN

QUEX_INLINE void
QUEX_CONVERTER_CHAR_DEF(cp866, utf32)(const QUEX_TYPE_CHARACTER** input_pp,
                                          uint32_t**                  output_pp)
{
    uint16_t             unicode = (uint32_t)0;
    QUEX_TYPE_CHARACTER  input   = *(*input_pp)++;
    if( input < 0x0000D1 ) {
        if( input < 0x0000C0 ) {
            if( input < 0x0000B8 ) {
                if( input < 0x0000B3 ) {
                    if( input < 0x000080 ) {
                        unicode = (uint32_t)input;
                    } else {
                    
                        if( input < 0x0000B0 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000390;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024E1;
                        }
                    }
                } else {
                
                    if( input < 0x0000B5 ) {
                        if( input < 0x0000B4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00244F;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002470;
                        }
                    } else {
                    
                        if( input < 0x0000B7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024AC;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        }
                    }
                }
            } else {
            
                if( input < 0x0000BC ) {
                    if( input < 0x0000BA ) {
                        if( input < 0x0000B9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AA;
                        }
                    } else {
                    
                        if( input < 0x0000BB ) {
                            unicode = (uint32_t)input + (uint32_t)0x002497;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249C;
                        }
                    }
                } else {
                
                    if( input < 0x0000BE ) {
                        if( input < 0x0000BD ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A1;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        }
                    } else {
                    
                        if( input < 0x0000BF ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002451;
                        }
                    }
                }
            }
        } else {
        
            if( input < 0x0000C8 ) {
                if( input < 0x0000C3 ) {
                    if( input < 0x0000C1 ) {
                        unicode = (uint32_t)input + (uint32_t)0x002454;
                    } else {
                    
                        if( input < 0x0000C2 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002473;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00246A;
                        }
                    }
                } else {
                
                    if( input < 0x0000C5 ) {
                        if( input < 0x0000C4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002459;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00243C;
                        }
                    } else {
                    
                        if( input < 0x0000C6 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002477;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002498;
                        }
                    }
                }
            } else {
            
                if( input < 0x0000CC ) {
                    if( input < 0x0000CA ) {
                        if( input < 0x0000C9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002492;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00248B;
                        }
                    } else {
                    
                        if( input < 0x0000CB ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249B;
                        }
                    }
                } else {
                
                    if( input < 0x0000CE ) {
                        if( input < 0x0000CD ) {
                            unicode = (uint32_t)input + (uint32_t)0x002494;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002483;
                        }
                    } else {
                    
                        if( input < 0x0000CF ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249E;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002498;
                        }
                    }
                }
            }
        }
    } else {
    
        if( input < 0x0000F1 ) {
            if( input < 0x0000DA ) {
                if( input < 0x0000D5 ) {
                    if( input < 0x0000D3 ) {
                        unicode = (uint32_t)input + (uint32_t)0x002493;
                    } else {
                    
                        if( input < 0x0000D4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002486;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002484;
                        }
                    }
                } else {
                
                    if( input < 0x0000D8 ) {
                        if( input < 0x0000D7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00247D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002494;
                        }
                    } else {
                    
                        if( input < 0x0000D9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002492;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00243F;
                        }
                    }
                }
            } else {
            
                if( input < 0x0000DE ) {
                    if( input < 0x0000DC ) {
                        if( input < 0x0000DB ) {
                            unicode = (uint32_t)input + (uint32_t)0x002432;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AD;
                        }
                    } else {
                    
                        if( input < 0x0000DD ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A8;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AF;
                        }
                    }
                } else {
                
                    if( input < 0x0000E0 ) {
                        if( input < 0x0000DF ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024B2;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024A1;
                        }
                    } else {
                    
                        if( input < 0x0000F0 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000360;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000311;
                        }
                    }
                }
            }
        } else {
        
            if( input < 0x0000F8 ) {
                if( input < 0x0000F4 ) {
                    if( input < 0x0000F2 ) {
                        unicode = (uint32_t)input + (uint32_t)0x000360;
                    } else {
                    
                        if( input < 0x0000F3 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000312;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000361;
                        }
                    }
                } else {
                
                    if( input < 0x0000F6 ) {
                        if( input < 0x0000F5 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000313;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000362;
                        }
                    } else {
                    
                        if( input < 0x0000F7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000318;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000367;
                        }
                    }
                }
            } else {
            
                if( input < 0x0000FC ) {
                    if( input < 0x0000FA ) {
                        if( input < 0x0000F9 ) {
                            unicode = (uint32_t)input - (uint32_t)0x000048;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002120;
                        }
                    } else {
                    
                        if( input < 0x0000FB ) {
                            unicode = (uint32_t)input - (uint32_t)0x000043;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00211F;
                        }
                    }
                } else {
                
                    if( input < 0x0000FE ) {
                        if( input < 0x0000FD ) {
                            unicode = (uint32_t)input + (uint32_t)0x00201A;
                        } else {
                        
                            unicode = (uint32_t)input - (uint32_t)0x000059;
                        }
                    } else {
                    
                        if( input < 0x0000FF ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A2;
                        } else {
                        
                            unicode = (uint32_t)input - (uint32_t)0x00005F;
                        }
                    }
                }
            }
        }
    }
    *(*output_pp)++ = unicode;

}

QUEX_INLINE void
QUEX_CONVERTER_CHAR_DEF(cp866, utf16)(const QUEX_TYPE_CHARACTER** input_pp,
                                          uint16_t**                  output_pp)
{
    uint32_t   unicode   = (uint32_t)0;
    uint32_t*  unicode_p = &unicode;

    QUEX_CONVERTER_CHAR(cp866, utf32)(input_pp, &unicode_p);
    *(*output_pp)++ = unicode;

}

QUEX_INLINE void
QUEX_CONVERTER_CHAR_DEF(cp866, utf8)(const QUEX_TYPE_CHARACTER**  input_pp, 
                                         uint8_t**                    output_pp)
{
    uint32_t            unicode = (uint32_t)-1;
    QUEX_TYPE_CHARACTER input   = *(*input_pp)++;
    
    if( input < 0x0000D1 ) {
        if( input < 0x0000C0 ) {
            if( input < 0x0000B8 ) {
                if( input < 0x0000B3 ) {
                    if( input < 0x000080 ) {
                        unicode = (uint32_t)input;
                        goto one_byte;
                    } else {
                    
                        if( input < 0x0000B0 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000390;
                            goto two_bytes;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024E1;
                            goto three_bytes;
                        }
                    }
                } else {
                
                    if( input < 0x0000B5 ) {
                        if( input < 0x0000B4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00244F;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002470;
                        }
                    } else {
                    
                        if( input < 0x0000B7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024AC;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        }
                    }goto three_bytes;
                }
            } else {
            
                if( input < 0x0000BC ) {
                    if( input < 0x0000BA ) {
                        if( input < 0x0000B9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AA;
                        }
                    } else {
                    
                        if( input < 0x0000BB ) {
                            unicode = (uint32_t)input + (uint32_t)0x002497;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249C;
                        }
                    }
                } else {
                
                    if( input < 0x0000BE ) {
                        if( input < 0x0000BD ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A1;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        }
                    } else {
                    
                        if( input < 0x0000BF ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002451;
                        }
                    }
                }goto three_bytes;
            }
        } else {
        
            if( input < 0x0000C8 ) {
                if( input < 0x0000C3 ) {
                    if( input < 0x0000C1 ) {
                        unicode = (uint32_t)input + (uint32_t)0x002454;
                    } else {
                    
                        if( input < 0x0000C2 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002473;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00246A;
                        }
                    }
                } else {
                
                    if( input < 0x0000C5 ) {
                        if( input < 0x0000C4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002459;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00243C;
                        }
                    } else {
                    
                        if( input < 0x0000C6 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002477;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002498;
                        }
                    }
                }
            } else {
            
                if( input < 0x0000CC ) {
                    if( input < 0x0000CA ) {
                        if( input < 0x0000C9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002492;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00248B;
                        }
                    } else {
                    
                        if( input < 0x0000CB ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249F;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00249B;
                        }
                    }
                } else {
                
                    if( input < 0x0000CE ) {
                        if( input < 0x0000CD ) {
                            unicode = (uint32_t)input + (uint32_t)0x002494;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002483;
                        }
                    } else {
                    
                        if( input < 0x0000CF ) {
                            unicode = (uint32_t)input + (uint32_t)0x00249E;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002498;
                        }
                    }
                }
            }goto three_bytes;
        }
    } else {
    
        if( input < 0x0000F1 ) {
            if( input < 0x0000DA ) {
                if( input < 0x0000D5 ) {
                    if( input < 0x0000D3 ) {
                        unicode = (uint32_t)input + (uint32_t)0x002493;
                    } else {
                    
                        if( input < 0x0000D4 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002486;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002484;
                        }
                    }
                } else {
                
                    if( input < 0x0000D8 ) {
                        if( input < 0x0000D7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x00247D;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002494;
                        }
                    } else {
                    
                        if( input < 0x0000D9 ) {
                            unicode = (uint32_t)input + (uint32_t)0x002492;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00243F;
                        }
                    }
                }goto three_bytes;
            } else {
            
                if( input < 0x0000DE ) {
                    if( input < 0x0000DC ) {
                        if( input < 0x0000DB ) {
                            unicode = (uint32_t)input + (uint32_t)0x002432;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AD;
                        }
                    } else {
                    
                        if( input < 0x0000DD ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A8;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024AF;
                        }
                    }goto three_bytes;
                } else {
                
                    if( input < 0x0000E0 ) {
                        if( input < 0x0000DF ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024B2;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x0024A1;
                        }goto three_bytes;
                    } else {
                    
                        if( input < 0x0000F0 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000360;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000311;
                        }goto two_bytes;
                    }
                }
            }
        } else {
        
            if( input < 0x0000F8 ) {
                if( input < 0x0000F4 ) {
                    if( input < 0x0000F2 ) {
                        unicode = (uint32_t)input + (uint32_t)0x000360;
                    } else {
                    
                        if( input < 0x0000F3 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000312;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000361;
                        }
                    }
                } else {
                
                    if( input < 0x0000F6 ) {
                        if( input < 0x0000F5 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000313;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000362;
                        }
                    } else {
                    
                        if( input < 0x0000F7 ) {
                            unicode = (uint32_t)input + (uint32_t)0x000318;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x000367;
                        }
                    }
                }goto two_bytes;
            } else {
            
                if( input < 0x0000FC ) {
                    if( input < 0x0000FA ) {
                        if( input < 0x0000F9 ) {
                            unicode = (uint32_t)input - (uint32_t)0x000048;
                            goto two_bytes;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x002120;
                            goto three_bytes;
                        }
                    } else {
                    
                        if( input < 0x0000FB ) {
                            unicode = (uint32_t)input - (uint32_t)0x000043;
                            goto two_bytes;
                        } else {
                        
                            unicode = (uint32_t)input + (uint32_t)0x00211F;
                            goto three_bytes;
                        }
                    }
                } else {
                
                    if( input < 0x0000FE ) {
                        if( input < 0x0000FD ) {
                            unicode = (uint32_t)input + (uint32_t)0x00201A;
                            goto three_bytes;
                        } else {
                        
                            unicode = (uint32_t)input - (uint32_t)0x000059;
                            goto two_bytes;
                        }
                    } else {
                    
                        if( input < 0x0000FF ) {
                            unicode = (uint32_t)input + (uint32_t)0x0024A2;
                            goto three_bytes;
                        } else {
                        
                            unicode = (uint32_t)input - (uint32_t)0x00005F;
                            goto two_bytes;
                        }
                    }
                }
            }
        }
    }


one_byte:
*((*output_pp)++) = (uint8_t)unicode;
return;
two_bytes:
*((*output_pp)++) = (uint8_t)(0xC0 | (unicode >> 6)); 
*((*output_pp)++) = (uint8_t)(0x80 | (unicode & (uint32_t)0x3f));
return;
three_bytes:
*((*output_pp)++) = (uint8_t)(0xE0 | unicode           >> 12);
*((*output_pp)++) = (uint8_t)(0x80 | (unicode & (uint32_t)0xFFF) >> 6);
*((*output_pp)++) = (uint8_t)(0x80 | (unicode & (uint32_t)0x3F));
return;

}

#define __QUEX_FROM           cp866
#define __QUEX_FROM_TYPE      QUEX_TYPE_CHARACTER

/* (1b) Derive converters to char and wchar_t from the given set 
 *      of converters. (Generator uses __QUEX_FROM and QUEX_FROM_TYPE)      */
#include <quex/code_base/converter_helper/generator/character-converter-to-char-wchar_t.gi>

/* (2) Generate string converters to utf8, utf16, utf32 based on the
 *     definitions of the character converters.                             */
#include <quex/code_base/converter_helper/generator/implementations.gi>

QUEX_NAMESPACE_MAIN_CLOSE

#endif /* __QUEX_INCLUDE_GUARD__CONVERTER_HELPER__cp866_I */

