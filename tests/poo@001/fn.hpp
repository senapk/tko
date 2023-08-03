#pragma once

#include <iostream>
#include <sstream>
#include <iomanip>
#include <array>
#include <set>
#include <map>
#include <vector>
#include <list>
#include <unordered_map>
#include <unordered_set>
#include <memory>

namespace fn {

using str_view = std::string_view;

//--------------------------------------------------------
//-------------------- ALIGN -------------- --------------
//--------------------------------------------------------

class Align {
    char align_mode { 0 }; //< > or ^, default is center
    int  align_size { 0 }; //size of the field
    char pad_char   { ' ' }; //char used to pad the field
    std::string format { "" }; //filtered format string

    bool extract_align() {
        std::string align_str_size;

        size_t i {0}, j {0};
        for (i = 0; i < format.size(); ++i) {
            if (format[i] == '<' || format[i] == '>' || format[i] == '^') { //achei o alinhamento
                this->align_mode = format[i];

                for (j = i + 1; j < format.size(); ++j) { //extraindo o tamanho do alinhamento
                    if (format[j] >= '0' && format[j] <= '9') {
                        align_str_size += format[j];
                    } else { // terminou o tamanho
                        break;
                    }
                }
                if (align_str_size.empty()) {
                    this->align_size = 0;
                    std::cout << "fail: format symbol `" << format[i] << "` must be followed by a size\n";
                    exit(1);
                }
                this->align_size = std::stoi(align_str_size);
                this->format.erase(i, j - i);
                return true;
            }
        }
        return false;
    }

    void extract_pad() {
        //search for : char in format, if exists and is followed by a char, then use that char as padding, and remove both from string
        auto pos = this->format.find(':');
        if (pos != std::string::npos) {
            if (pos + 1 < format.size()) {
                this->pad_char = format[pos + 1];
                this->format.erase(pos, 2);
            } else {
                std::cout << "fail: format symbol `:` must be followed by a padding char\n";
                exit(1);
            }
        }
    }
public:

    Align(str_view format) {
        this->format = format;
        this->extract_pad();
        this->extract_align();
    }

    std::string align_text(const std::string& str) {
        int len = str.length();
        if(this->align_mode == 0 || this->align_size < len) { 
            return str; 
        }
        int diff = this->align_size - len;
        
        //default is center
        int padleft = diff/2;
        int padright = diff - padleft;
        if(this->align_mode == '>') {
            padleft = diff;
            padright = 0;
        }
        else if(this->align_mode == '<') {
            padleft = 0;
            padright = diff;
        }
        return std::string(padleft, this->pad_char) + str + std::string(padright, this->pad_char);
    }

    const std::string& get_filtered_format() {
        return this->format;
    }
    int get_align_size() {
        return this->align_size;
    }
    char get_pad_char() {
        return this->pad_char;
    }
    char get_align_mode() {
        return this->align_mode;
    }
};

//--------------------------------------------------------
//-------------------- CFMT  -----------------------------
//--------------------------------------------------------

class CFMT {

    //transformation using sprintf
    template <typename T>
    static std::string c_transform(const T& data, const str_view& format) {
        std::string fmt(format);
        auto size = std::snprintf(nullptr, 0, fmt.c_str(), data);
        std::string output(size + 1, '\0');
        std::sprintf(&output[0], fmt.c_str(), data);
        if (output.back() == '\0') 
            output.pop_back();
        return output;
    }

    //conversion to string using stringstream
    template <typename T>
    static std::string sstream_transform(const T& data) {
        std::stringstream ss;
        ss << data;
        return ss.str();
    }


    template <typename T>
    static std::string process(const T& data, const str_view& format) 
    {
        if (format == "%s" || format == "") {
            return sstream_transform(data);
        }
        if (format.size() > 0 && format.find("%s") != std::string::npos) {//formatting a non string with %s
            return process(sstream_transform(data), format);
        }
        return c_transform(data, format);
    }

    //validate if the format is correct for a string
    static std::string process(const std::string& data, const str_view& format) 
    {
        return process(data.c_str(), format);
    }
    
    //validate if the format is correct for a const char *
    //write specialization for const char *
    static std::string process(const char* const& data, const str_view& format) 
    {
        if (format == "%s" || format == "") {
            return data;
        }
        return CFMT::c_transform(data, format);
    };

    
public:

    template <typename T>
    static std::string format(const T& data, const str_view& format) 
    {
        Align align(format);
        std::string filtered = align.get_filtered_format();
        return align.align_text(process(data, filtered));
    }

};

//--------------------------------------------------------
//-------------------- TOSTR PROTOTYPE -------------------
//--------------------------------------------------------

//[[tostr]]
/**
 * Converte o dado passado em string.
 * 
 * Se passado o parâmetro de formatação cfmt, o dado será formatado usando o modelo do printf.
 * Se o dado for um container, o formato será aplicado em todos os elementos
 * do container recursivamente.
 * 
 * vectors, lists e arrays são impressos entre colchetes.
 * maps e sets são impressos entre chaves.
 * pairs e tuples são impressos entre parênteses.
 * 
 * Para classe do usuário ser impressa, ela deve sobrecarregar o ostream& operador <<.
 * 
 * @param data Dado a ser convertido
 * @param cfmt (opcional) Parâmetro de formatação no modo printf
 * @return String com o dado convertido
 * 
 * @warning tostr(std::list<int>{1,2,3}, "%02d") | WRITE();
 * 
 * @note https://github.com/senapk/cppaux#tostr
 */
template <typename T> std::string tostr(const T& t     , const str_view& format = "");
//[[tostr]]

//--------------------------------------------------------
//-------------------- JOIN  I----------------------------
//--------------------------------------------------------

namespace hide {
template <typename CONTAINER> 
std::string __join(const CONTAINER& container, const str_view& separator, const str_view& cfmt) 
{ 
    std::stringstream ss;
    for (auto it = container.begin(); it != container.end(); ++it) {
        ss << (it == container.begin() ? "" : separator);
        ss << tostr(*it, cfmt);
    }
    return ss.str();
}

template <typename... Ts>
std::string __join(std::tuple<Ts...> const &the_tuple, const str_view& separator, const str_view& cfmt)
{
    std::stringstream ss;
    std::apply( [&](Ts const &...tuple_args) {
            std::size_t n{0};
            ((ss << tostr(tuple_args, cfmt) << (++n != sizeof...(Ts) ? separator : "")), ...);
        }, the_tuple);
    return ss.str();
}

template <typename T1, typename T2>
std::string __join(const std::pair<T1, T2>& the_pair, const str_view& separator, const str_view& cfmt)
{
    std::stringstream ss;
    ss << tostr(the_pair.first, cfmt) << separator << tostr(the_pair.second, cfmt);
    return ss.str();
}
}
//[[join]]
/**
 * Transforma um container, par ou tupla em string, separando os elementos
 * pelo separador e envolvendo com os brakets.
 *
 * Se os elementos não forem strings, eles serão transformados em string utilizando
 * a função tostr.
 * 
 * @param container Container a ser transformado em string
 * @param separator Separador entre os elementos
 * @param cfmt      Formato para cada elemento
 * @return string com os elementos concatenados
 * 
 * @warning join(std::vector<int>{1,2,3}, " ") | WRITE(); // "1 2 3"
 * 
 * @note https://github.com/senapk/cppaux#join
 */
template <typename T>
std::string join(const T& t, const str_view& separator = "", const str_view& cfmt = "") 
//[[join]]
{
    return hide::__join(t, separator, cfmt);
}

//class
struct JOIN {
    str_view delimiter;
    str_view cfmt;
    JOIN(const str_view& delimiter = "", const str_view& cfmt = "") : delimiter(delimiter), cfmt(cfmt) {}
    template <typename CONTAINER> std::string operator()(const CONTAINER& v) const { return join(v, delimiter, cfmt); }
    template <typename T> friend std::string operator|(const T& v, const JOIN& obj) { return obj(v); }
};

//--------------------------------------------------------
//-------------------- TOSTR -----------------------------
//--------------------------------------------------------

namespace hide {
template <typename T>             inline std::string __tostr(const T& t                      , const str_view& format) { return CFMT::format(t, format); }
                                  inline std::string __tostr(int i                           , const str_view& format) { return CFMT::format(i, format); }
                                  inline std::string __tostr(bool b                          , const str_view& format) { (void) format; return b ? "true" : "false"; }
                                  inline std::string __tostr(const char* s                   , const str_view& format) { return CFMT::format(s, format); }
                                  inline std::string __tostr(const std::string& s            , const str_view& format) { return CFMT::format(s, format); }
                                  inline std::string __tostr(const str_view& s               , const str_view& format) { return CFMT::format(s, format); }
template <typename A, typename B> inline std::string __tostr(const std::pair<A,B>& p         , const str_view& format) { return "(" + tostr(p.first, format) + ", " + tostr(p.second, format) + ")"; }
template <typename T>             inline std::string __tostr(const std::list<T>& t           , const str_view& format) { return "[" + join(t, ", ", format) + "]"; }
template <typename T>             inline std::string __tostr(const std::vector<T>& t         , const str_view& format) { return "[" + join(t, ", ", format) + "]"; }
template <typename ...Ts>         inline std::string __tostr(const std::tuple<Ts...>& t      , const str_view& format) { return "(" + join(t, ", ", format) + ")"; }
template <typename T, size_t N>   inline std::string __tostr(const std::array<T, N>& t       , const str_view& format) { return "[" + join(t, ", ", format) + "]"; }
template <typename T>             inline std::string __tostr(const std::set<T>& t            , const str_view& format) { return "{" + join(t, ", ", format) + "}"; }
template <typename K, typename T> inline std::string __tostr(const std::map<K,T>& t          , const str_view& format) { return "{" + join(t, ", ", format) + "}"; }
template <typename T>             inline std::string __tostr(const std::unordered_set<T>& t  , const str_view& format) { return "{" + join(t, ", ", format) + "}"; }
template <typename K, typename T> inline std::string __tostr(const std::unordered_map<K,T>& t, const str_view& format) { return "{" + join(t, ", ", format) + "}"; }
template <typename T>             inline std::string __tostr(const std::shared_ptr<T>& t     , const str_view& format) { return t == nullptr ? "null" : tostr(*t, format); }

}
//wrapper function
template <typename T> std::string tostr(const T& t     , const str_view& cfmt) { return hide::__tostr(t, cfmt); }
//class
struct TOSTR {
    str_view cfmt;

    TOSTR(const str_view& cfmt = "") : cfmt(cfmt) {}

    template <typename T> std::string operator()(const T& t) const { return tostr(t, cfmt); }
    template <typename T> friend std::string operator|(const T& v, const TOSTR& obj) { return obj(v); }
};

//--------------------------------------------------------
//-------------------- FORMAT ----------------------------
//--------------------------------------------------------

//class
template<typename... Args> 
class FORMAT 
{
    std::tuple<Args...> args;

    std::vector<std::string> tuple_to_vector_str(const std::vector<std::string>& controls)
    {
        std::vector<std::string> result;
        std::apply
        (
            [&result, &controls](Args const&... tupleArgs)
            {
                int i = -1;
                ((result.push_back(tostr(tupleArgs, controls.at(++i)))), ...);
            }, this->args
        );

        return result;
    }

    std::pair<std::vector<std::string>, std::vector<std::string>> extract(std::string data)
    {
        data.append("_");
        auto lim = data.size() - 1;
        std::vector<std::string> texts = {""};
        std::vector<std::string> ctrls = {""};
        auto* destiny = &texts;

        for (size_t i = 0; i < lim;) {
            char c = data[i];
            if ((c == '{' && data[i + 1] == '{') || (c == '}' && data[i + 1] == '}'))
            {
                destiny->back().append(std::string(1, c));
                i += 2;
            }
            else if (c == '{') 
            {
                texts.push_back("");
                destiny = &ctrls;
                i++;
            }
            else if (c == '}') 
            {
                ctrls.push_back("");
                destiny = &texts;
                i++;
            }
            else
            {
                destiny->back().append(std::string(1,c));
                i++;
            }
        }
        while (texts.size() > ctrls.size())
            ctrls.push_back("");
        return {texts, ctrls};
    }

public:

    FORMAT(Args ...args): args(std::forward<Args>(args)...){}

    std::string operator()(std::string fmt)
    {
        auto [texts, controls] = extract(fmt);
        try {
            auto vars = tuple_to_vector_str(controls);
            
            if(vars.size() < texts.size() - 1) {
                throw std::out_of_range("");
            }
            std::stringstream ss;
            for (size_t i = 0; i < vars.size(); i++)
                ss << texts[i] << vars[i];
            ss << texts.back(); //ultimo texto
            return ss.str();
        } catch (std::out_of_range& e) {
            std::cout << "fail: verifique a quantidade de parâmetros passado para string: " << fmt << '\n';
            exit(1);
        }
    }

    friend std::string operator|(std::string fmt, FORMAT<Args...> obj) { return obj(fmt); }
};

//[[format]]
/**
 * Formata uma string com base nos argumentos passados utilizando um modelo de chaves para posicionar os argumentos.
 * Se dentro da chave, houver um string de formatação, o dado será formatado com base nela.
 * Não primitivos são formatados de acordo com a função TOSTR
 * 
 * @param fmt O texto com os {} para substituir pelos argumentos
 * @param Args Os argumentos a serem substituídos
 * @return O texto formatado
 * 
 * @warning format("O {} é {0.2f} e o {} é {0.2f}", "pi", 3.141592653, "e", 2.7182818);
 * @note https://github.com/senapk/cppaux#format
 * 
 */
template<typename... Args> std::string format(std::string fmt, Args ...args) 
//[[format]]
{
    return FORMAT<Args...>(args...)(fmt); 
}


//--------------------------------------------------------
//-------------------- PRINT------------------------------
//--------------------------------------------------------

//[[print]]
/**
 * Invoca a função format e imprime o resultado na tela
 * 
 * @param fmt O texto com os {} para substituir pelos argumentos
 * @param Args Os argumentos a serem substituídos
 * @return O texto formatado
 * 
 * @warning print("O {} é {0.2f} e o {} é {0.2f}", "pi", 3.141592653, "e", 2.7182818);
 * @note https://github.com/senapk/cppaux#print
 * 
 */
template<typename... Args> std::string print(std::string fmt, Args ...args)
//[[print]]
{ 
    auto result = FORMAT<Args...>(args...)(fmt);
    std::cout << result;
    return result;
}
//class
template<typename... Args> 
struct PRINT {
    std::tuple<Args...> args;
    PRINT(Args ...args): args(std::forward<Args>(args)...) { }
    std::string operator()(std::string fmt) { return print(fmt, args); }
    friend std::string operator|(std::string fmt, PRINT<Args...> obj) { return obj(fmt); }
};

//--------------------------------------------------------
//-------------------- WRITE -----------------------------
//--------------------------------------------------------

//[[write]]
/**
 * Tranforma um dado em string utilizando a função tostr e envia para o std::cout quebrando a linha.
 * 
 * @param data Dado a ser transformado em string
 * @param end (opcional) String de finalização
 * @return Dado original
 * 
 * @warning write(std::vector<int> {1, 2, 3}); // [1, 2, 3]
 * 
 * @note https://github.com/senapk/cppaux#write
 */
template <typename PRINTABLE> const PRINTABLE& write(const PRINTABLE& data, str_view end = "\n") 
//[[write]]
{
    std::cout << tostr(data) << end;
    return data;
}

//class
struct WRITE {
    str_view end;
    WRITE(str_view end = "\n"): end(end) { }

    template <typename PRINTABLE>        const PRINTABLE& operator()(const PRINTABLE& data           ) { return write(data, end); }
    template <typename PRINTABLE> friend const PRINTABLE& operator| (const PRINTABLE& data, WRITE obj) { return obj(data); }
};

//--------------------------------------------------------
//-------------------- SLICE -----------------------------
//--------------------------------------------------------

class SLICE {
public:
    SLICE(int begin = 0) {
        this->from_begin = begin == 0;
        this->begin = begin;
        this->to_end = true;
    }
    SLICE(int begin, int end) {
        this->begin = begin;
        this->end = end;
        this->from_begin = false;
        this->to_end = false;
    }
    template<typename CONTAINER>
    auto operator()(const CONTAINER& container) const {
        auto aux = SLICE::new_vec_from(container);
        
        //empty container
        if (!this->from_begin && !this->to_end && (this->begin == this->end)) {
            return aux;
        }

        //full container
        if (this->from_begin && this->to_end) {
            std::copy(container.begin(), container.end(), std::back_inserter(aux));
            return aux;
        }

        int size = container.size();
        int begin = 0;
        int end = size;
        if (!this->from_begin) {
            begin = this->begin;
            if (begin < 0)
                begin = size + begin;
            begin = std::min(begin, size);
        }
        if (!this->to_end) {
            end = this->end;
            if (end < 0)
                end = size + end;
            end = std::min(end, size);
        }

        std::copy(std::next(container.begin(), begin), std::next(container.begin(), end), std::back_inserter(aux));
        return aux;
    }
    
    template<typename CONTAINER> friend auto operator|(const CONTAINER& container, const SLICE& obj) { return obj(container); }

private:
    int begin;
    int end;
    bool from_begin {false};
    bool to_end {false};

    template<typename CONTAINER>
    static auto new_vec_from(const CONTAINER& container) {
        auto fn = [](auto x) {return x;}; 
        std::vector<decltype(fn(*container.begin()))> aux;
        return aux;
    }

    template <typename K, typename T>
    static auto new_vec_from(const std::map<K, T>& container) {
        auto fn = [](auto x) {return x;}; 
        std::vector<std::pair<decltype(fn(container.begin()->first)), decltype(fn(container.begin()->second))>> aux;
        return aux;
    }

    template <typename K, typename T>
    static auto new_vec_from(const std::unordered_map<K, T>& container) {
        auto fn = [](auto x) {return x;}; 
        std::vector<std::pair<decltype(fn(container.begin()->first)), decltype(fn(container.begin()->second))>> aux;
        return aux;
    }

};

//[[slice]]
/**
 * Fatia um container de begin até o fim retornando um vector com os elementos copiados.
 * O funcionamento é equivalente à função slice do Python ou do Javascript. Se não passado
 * nenhum parâmetro, copia todos os elementos. Os índices podem ser negativos para indicar
 * que a contagem deve ser feita a partir do final.
 * 
 * @param container Container a ser fatiado
 * @param begin (opcional) Índice inicial
 * @return Vector com os elementos copiados
 * 
 * @warning std::vector<int>{1, 2, 3, 4, 5} | SLICE(1)  | WRITE(); // [2, 3, 4, 5]
 * 
 * @note https://github.com/senapk/cppaux#slice
*/
template<typename CONTAINER>
auto slice(const CONTAINER& container, int begin = 0)
//[[slice]]
{
    return SLICE(begin)(container);
}


/**
 * Fatia um container de begin até o fim retornando um vector com os elementos copiados.
 * O funcionamento é equivalente à função slice do Python ou do Javascript. Se não passado
 * nenhum parâmetro, copia todos os elementos. Os índices podem ser negativos para indicar
 * que a contagem deve ser feita a partir do final.
 * 
 * @param container Container a ser fatiado
 * @param begin Índice inicial
 * @param end Índice final
 * @return Vector com os elementos copiados
 * 
 * @warning std::vector<int>{1, 2, 3, 4, 5} | SLICE(1, -1)  | WRITE(); // [2, 3, 4]
 * 
 * @note https://github.com/senapk/cppaux#slice
*/
template<typename CONTAINER>
auto slice(CONTAINER container, int begin, int end)
{
    return SLICE(begin, end)(container);
}

//--------------------------------------------------------
//-------------------- MAP   -----------------------------
//--------------------------------------------------------

//[[map]]
/**
 * Retorna um vetor com o resultado da aplicação da função fn para cada elemento do container
 * 
 * @param container Container a ser mapeado
 * @param fn Função a ser aplicada em cada elemento do container
 * @return Vector com os elementos resultantes da aplicação da função
 * 
 * @note https://github.com/senapk/cppaux#map
 */
template<typename CONTAINER, typename FUNCTION>
auto map(const CONTAINER& container, FUNCTION fn)
//[[map]]
{
    std::vector<decltype(fn(*container.begin()))> aux;
    for (const auto& item : container)
        aux.push_back(fn(item));
    return aux;
}

template <typename FUNCTION>
struct MAP {
    FUNCTION fn;
    MAP(FUNCTION fn) : fn(fn) {};
    template<typename CONTAINER> auto operator()(const CONTAINER& container) const { return map(container, fn); }
    template<typename CONTAINER> friend auto operator|(const CONTAINER& container, const MAP& map) { return map(container); }
};

//--------------------------------------------------------
//-------------------- FILTER ----------------------------
//--------------------------------------------------------

//[[filter]]
/**
 * Retorna um vetor com os elementos do container que satisfazem a função predicado fn
 * @param container Container a ser filtrado
 * @param fn Função predicado
 * @return Vector com os elementos que satisfazem a função predicado
 * 
 * @note https://github.com/senapk/cppaux#filter
 */
template<typename CONTAINER, typename FUNCTION>
auto filter(const CONTAINER& container, FUNCTION fn)
//[[filter]]
{
    auto aux = slice(container, 0, 0);
    for(const auto& x : container) {
        if(fn(x))
            aux.push_back(x);
    }
    return aux;
}

template <typename FUNCTION>
struct FILTER {
    FUNCTION fn;
    FILTER(FUNCTION fn) : fn(fn) {};
    template<typename CONTAINER> auto operator()(const CONTAINER& container) const { return filter(container, fn); }
    template<typename CONTAINER> friend auto operator|(const CONTAINER& container, const FILTER& obj) { return obj(container); }
};

//--------------------------------------------------------
//-------------------- RANGE -----------------------------
//--------------------------------------------------------

// [[range]]
/**
 * @brief Gera um vetor de inteiros de init até end, mas não incluindo end, com passo step.
 * 
 * @param init início
 * @param end limite superior
 * @param step passo do incremento
 * @return vetor de inteiros
 * 
 * @warning range(0, 10, 2) | WRITE(); // [0, 2, 4, 6, 8]
 * 
 * @note https://github.com/senapk/cppaux#range
*/
inline std::vector<int> range(int init, int end, int step = 1)
//[[range]]
{
    if (step == 0)
        throw std::runtime_error("step cannot be zero");
    std::vector<int> aux;
    if (step > 0) {
        for (int i = init; i < end; i += step) {
            aux.push_back(i);
        }
    } else {
        for (int i = init; i > end; i += step) {
            aux.push_back(i);
        }
    }
    return aux;
}

/**
 * @brief Gera um vetor de inteiros de 0 até end, mas não incluindo end, com passo step
 * 
 * @param end limite superior
 * @param step passo do incremento
 * @return vetor de inteiros
 * 
 * @warning range(10) | WRITE(); // [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
 * 
 * @note https://github.com/senapk/cppaux#range
*/
inline std::vector<int> range(int end) {
    return range(0, end, 1);
}

struct RANGE {
    RANGE() : init(0), step(1) {};

    std::vector<int> operator()(int end) const {
        return range(init, end, step);
    }

    friend std::vector<int> operator|(int end, const RANGE& obj) {
        return obj(end);
    }

    int init {0};
    int end {0};
    int step {0};
};

//--------------------------------------------------------
//-------------------- ENUMERATE -------------------------
//--------------------------------------------------------

//[[enumerate]]
/**
 * Retorna um vetor de pares com os indices seguidos dos elementos originais do vetor
 * 
 * @param container Container a ser enumerado
 * @return Vector com os pares
 * 
 * @note https://github.com/senapk/cppaux#enumerate
 */
template<typename CONTAINER>
auto enumerate(const CONTAINER& container)
//[[enumerate]]
{
    auto fn = [](auto x) {return x;}; 
    std::vector<std::pair<int, decltype(fn(*container.begin()))>> aux;
    int i = 0;
    for (const auto& item : container) {
        aux.push_back(std::make_pair(i, item));
        i++;
    }
    return aux;
}

struct ENUMERATE {
    template<typename CONTAINER> auto operator()(const CONTAINER& container) const { return enumerate(container); }
    template<typename CONTAINER> friend auto operator|(const CONTAINER& container, const ENUMERATE& obj) { return obj(container); }
};



//--------------------------------------------------------
//-------------------- STRTO -----------------------------
//--------------------------------------------------------

//[[strto]]
/**
 * Transforma de string para o tipo solicitado utilizando o operador de extração de stream.
 * Dispara uma exceção caso a conversão não seja possível.
 * 
 * @param value String a ser convertida
 * @tparam READABLE Tipo a ser convertido
 * @return Valor convertido
 * @throws std::runtime_error Caso a conversão não seja possível
 * 
 * @note https://github.com/senapk/cppaux#strto
 * 
*/
template <typename READABLE>
READABLE strto(std::string value)
//[[strto]]
{
    std::istringstream iss(value);
    READABLE aux;
    if (iss >> aux) {
        return aux;
    }
    throw std::runtime_error("strto: invalid conversion from " + value);
}

template <typename READABLE>
struct STRTO {
    READABLE operator()(std::string value) const { return strto<READABLE>(value); }
    friend READABLE operator|(std::string value, const STRTO& obj) { return obj(value); }
};

//--------------------------------------------------------
//-------------------- NUMBER ----------------------------
//--------------------------------------------------------

//[[number]]
/**
 * Transforma de string para double utilizando a função strto.
 * 
 * @param value String a ser convertida
 * @return Valor convertido para double
 * @throws std::runtime_error Caso a conversão não seja possível
 * 
 * @note https://github.com/senapk/cppaux#number
 * 
*/
inline double number(std::string value)
//[[number]]
{
    return strto<double>(value);
}

struct NUMBER {
    double operator()(std::string value) const { return number(value); }
    friend double operator|(std::string value, const NUMBER& obj) { return obj(value); }
};

//--------------------------------------------------------
//-------------------- UNPACK -----------------------------
//--------------------------------------------------------

template <typename... Types>
struct UNPACK {
    char delimiter;
    UNPACK(char delimiter) : delimiter(delimiter) {}

    template<typename Head, typename... Tail>
    std::tuple<Head, Tail...> tuple_read_impl(std::istream& is, char delimiter) const {
        Head val;
        std::string token;
        std::getline(is, token, delimiter);
        std::stringstream ss_token(token);
        ss_token >> val;
        if constexpr (sizeof...(Tail) == 0) // this was the last tuple value
            return std::tuple{val};
        else
            return std::tuple_cat(std::tuple{val}, tuple_read_impl<Tail...>(is, delimiter));
    }

    std::tuple<Types...> operator()(std::string content) const {
        std::stringstream ss(content);
        return tuple_read_impl<Types...>(ss, this->delimiter);
    }
    
    friend std::tuple<Types...> operator|(std::string content, const UNPACK& obj) {
        return obj(content);
    }
};

//[[unpack]]
/**
 * Transforma de string para tupla dados os tipos de cada elemento e o char separador.
 * 
 * @tparam TS... Tipos a serem extraídos
 * @param value String a ser convertida
 * @param delimiter Caractere separador entre os elementos
 * @return Tupla com os elementos convertidos
 * 
 * @warning unpack<int, double, std::string>("1:2.4:uva", ':') | WRITE(); // (1, 2.4, "uva")
 * 
 * @note https://github.com/senapk/cppaux#unpack
 * 
 */
template <typename... TS>
std::tuple<TS...> unpack(const std::string& line, char delimiter)
//[[unpack]]
{
    return UNPACK<TS...>(delimiter)(line);
}


//--------------------------------------------------------
//-------------------- ZIP   -----------------------------
//--------------------------------------------------------

//[[zip]]
/**
 * Une dois containers em um vetor de pares limitado ao menor tamanho dos dois containers.
 * 
 * @param container_a primeiro container
 * @param container_b segundo container
 * @return Vetor de pares
 * 
 * @warning zip(vector<int>{1, 2, 3}, string("pterodactilo")) | WRITE(); //[(1, p), (2, t), (3, e)]
 * 
 * @note https://github.com/senapk/cppaux#zip
 */
template<typename CONTAINER_A, typename CONTAINER_B>
auto zip(const CONTAINER_A& A, const CONTAINER_B& B)
//[[zip]]
{
    auto fn = [](auto x) { return x; };
    using type_a = decltype(fn(*A.begin()));
    using type_b = decltype(fn(*B.begin()));
    std::vector<std::pair<type_a, type_b>> aux;

    auto ita = A.begin();
    auto itb = B.begin();
    while(ita != A.end() &&  itb != B.end()) {
        aux.push_back({*ita, *itb});
        ita++;
        itb++;
    }
    return aux;
};

template <typename CONTAINER_B>
struct ZIP {
    CONTAINER_B container_b;
    ZIP(const CONTAINER_B& container_b) : container_b(container_b) {}

    template<typename CONTAINER_A>
    auto operator()(const CONTAINER_A& container_a) const { return zip(container_a, container_b); }
    template<typename CONTAINER_A>
    friend auto operator|(const CONTAINER_A& container_a, const ZIP& obj) { return obj(container_a); }
};

//--------------------------------------------------------
//-------------------- ZIPWITH ---------------------------
//--------------------------------------------------------

//[[zipwith]]
/**
 * Une dois containers em um único container limitado ao menor tamanho dos dois containers
 * colocando o resultado da função fnjoin em cada par no container de saída.
 * 
 * @param container_a primeiro container
 * @param container_b segundo container
 * @return Vetor com os resultados
 * 
 * @warning zipwith(range(10), "pterodactilo"s, [](auto x, auto y) { return tostr(x) + y; }) | WRITE(); // ["0p", "1t", "2e", "3r", "4o", "5d", "6a", "7c", "8t", "9i"]
 * @note https://github.com/senapk/cppaux#zipwith
 * 
 */
template<typename CONTAINER_A, typename CONTAINER_B, typename FNJOIN>
auto zipwith(const CONTAINER_A& A, const CONTAINER_B& B, FNJOIN fnjoin)
//[[zipwith]]
{
    auto idcopy = [](auto x) { return x; };
    using type_out = decltype( fnjoin( idcopy(*A.begin()), idcopy(*B.begin()) ));
    std::vector<type_out> aux;

    auto ita = A.begin();
    auto itb = B.begin();
    while(ita != A.end() &&  itb != B.end()) {
        aux.push_back(fnjoin(*ita, *itb));
        ita++;
        itb++;
    }
    return aux;
};


template<typename CONTAINER_B, typename FNJOIN>
struct ZIPWITH {
    CONTAINER_B container_b;
    FNJOIN fnjoin;
    ZIPWITH(const CONTAINER_B& container_b, FNJOIN fnjoin) : container_b(container_b), fnjoin(fnjoin) {}

    template<typename CONTAINER_A>        auto operator()(const CONTAINER_A& container_a) const { return zipwith(container_a, container_b, fnjoin); }
    template<typename CONTAINER_A> friend auto operator| (const CONTAINER_A& container_a, const ZIPWITH& obj) { return obj(container_a); }
};

//--------------------------------------------------------
//-------------------- SPLIT -----------------------------
//--------------------------------------------------------

//[[split]]
/**
 * Transforma uma string em um vetor de strings, separando pelo delimitador
 * 
 * @param content String a ser separada
 * @param delimiter (opcional) Caractere delimitador
 * @return Vetor de strings
 * 
 * @warning split("a,b,c", ',') | WRITE(); // [a, b, c]
 * 
 * @note https://github.com/senapk/cppaux#split
 */
inline std::vector<std::string> split(std::string content, char delimiter = ' ')
//[[split]]
{
    std::vector<std::string> aux;
    std::string token;
    std::istringstream tokenStream(content);
    while (std::getline(tokenStream, token, delimiter))
        aux.push_back(token);
    return aux;
}

struct SPLIT {
    char delimiter;
    SPLIT(char delimiter = ' ') : delimiter(delimiter) {}

    std::vector<std::string>        operator()(std::string content) const { return split(content, delimiter); }
    friend std::vector<std::string> operator| (std::string content, const SPLIT& obj) { return obj(content); }
};

//--------------------------------------------------------
//-------------------- INPUT -----------------------------
//--------------------------------------------------------

//[[input]]
/**
 * Extrai uma linha inteira e retorna como string
 * O padrão é o std::cin, mas pode ser um fluxo ou arquivo
 * Se não houver mais linhas, lança uma exceção
 * 
 * @param source (opcional) de onde ler a linha
 * @return linha lida
 * 
 * @warning auto line = input();
 * 
 * @note https://github.com/senapk/cppaux#input
 */
inline std::string input(std::istream & is = std::cin)
//[[input]]
{
    std::string line;
    if (std::getline(is, line))
        return line;
    throw std::runtime_error("input empty");
}

struct INPUT {
    INPUT() {}

    std::string        operator()(std::istream& is = std::cin) const { return input(is); }
    friend std::string operator| (std::istream& is, const INPUT& obj) { return obj(is); }
};

} // namespace fn

using namespace std::string_literals;

//Transforma uma string em um double utilizando a função STRTO
inline double operator+(std::string text) {
    return fn::number(text);
}
