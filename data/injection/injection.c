#include "injection.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#include <time.h>

#define __USE_GNU
#include <dlfcn.h>

static FILE *finstrument_fp = NULL;

static void fprint_dlinfo(void *this_fn, void *call_site, char flag)
	__attribute__ ((no_instrument_function));

void main_constructor(void)
{
	/*
	 * Write result to disk.
	 * Close at exit.
	 */
	finstrument_fp = fopen("finstrument.txt", "w");
	if (finstrument_fp == NULL)
	{
		fprintf(stderr, "Fail to create finstrument.txt.\n");
		exit(EXIT_FAILURE);
	}
}

void main_destructor(void)
{
	fclose(finstrument_fp);
}

void __cyg_profile_func_enter(void *this_fn, void *call_site)
{
	fprint_dlinfo(this_fn, call_site, 'E');
}

void __cyg_profile_func_exit(void *this_fn, void *call_site)
{
	fprint_dlinfo(this_fn, call_site, 'X');
}

static void fprint_dlinfo(void *this_fn, void *call_site, char flag)
{
	Dl_info info = { 0 };
	dladdr(this_fn, &info);
	struct timespec spec;
	clock_gettime(CLOCK_REALTIME, &spec);
	fprintf(finstrument_fp, "%p %p %c %ld\n",
			(this_fn - info.dli_fbase),
			(call_site - info.dli_fbase),
			flag, spec.tv_nsec);
}
