#include <stdio.h>
#include <muParser/muParser.h>

int main()
{
	mu::Parser p;
	printf("Successfully initialized muParser %s\n", p.GetVersion().c_str());
	return 0;
}
