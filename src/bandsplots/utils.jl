using JSON
using PGFPlotsX
using PyCall
include("parameters.jl")

function read_calcfile(dir::String)
    json_data = JSON.parsefile(dir)
    return json_data
end

function update_parameters(params::Dict, key, value)
    if haskey(params, key)
        params[key] = value
    else
        error("$key does not exist in parameters!")
    end
end

function plot_params(params::Dict)
    for (key,value) in default_params
        if !haskey(params,key)
            params[key] = value
        end
    end
    if params["initial_band"] == 1
        println("The number of initial band can't be equal to 1, this parameter will be changed to 2! ")
        params["initial_band"] = 2

    elseif params["initial_band"] == params["final_band"]
        println("The number of bands are equal!....")
        println("Therefore we plot the number of ini_band + 1, check this in your parameters!")
        params["final_band"] = params["inital_band"] + 1

    elseif params["final_band"] < params["initial_band"]
        println("The number of final band to plot is less than initial bands!...")
        println("The end band parameter is now ini_band +1!")
        params["final_band"] = params["inital_band"] + 1
    end
    return params
end


function conditional_parameters(bands::Array,parameters::Dict)
    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!\n
                Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end
    return parameters
end
