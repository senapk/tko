package main

import (
	"fmt"
)

func join[T any](slices []T, sep string) string {
	var result string
	for i, v := range slices {
		if i != 0 {
			result += sep
		}
		result += fmt.Sprintf("%v", v)
	}
	return result
}

func print_slice[T any](slice []T) {
	if len(slice) == 0 {
		fmt.Println("N")
	} else {
		fmt.Println(join(slice, " "))
	}
}

func main() {
	var qtd_total, qtd_baruel int
	fmt.Scan(&qtd_total, &qtd_baruel)

	var fig_baruel []int
	for i := 0; i < qtd_baruel; i++ {
		var num int
		fmt.Scan(&num)
		fig_baruel = append(fig_baruel, num)
	}

	unicos_baruel := make(map[int]bool)
	var repetidos_baruel []int
	for _, fig := range fig_baruel {
		_, ok := unicos_baruel[fig]
		if ok {
			repetidos_baruel = append(repetidos_baruel, fig)
		} else {
			unicos_baruel[fig] = true
		}
	}
	print_slice(repetidos_baruel)

	var fig_faltantes []int
	for i := 1; i <= qtd_total; i++ {
		_, found := unicos_baruel[i]
		if !found {
			fig_faltantes = append(fig_faltantes, i)
		}
	}
	print_slice(fig_faltantes)
}
