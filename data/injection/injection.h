#ifndef INJECTION_H
#define INJECTION_H
void __cyg_profile_func_enter(void *this_fn, void *call_site)
	__attribute__ ((no_instrument_function));
void __cyg_profile_func_exit(void *this_fn, void *call_site)
	__attribute__ ((no_instrument_function));
void main_constructor(void)
	__attribute__ ((no_instrument_function, constructor));
void main_destructor(void)
	__attribute__ ((no_instrument_function, destructor));
#endif
