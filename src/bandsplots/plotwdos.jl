include("utils.jl")
include("parameters.jl")
include("build.jl")

function plotwdos(dir_calc::String,params::Dict,build::Bool=false)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    dos         = np.array(data["dos"])
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name2plot"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 
    psize = 0.5
    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!")
        println("Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end
    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    plot = @pgf TikzPicture(
        Axis(
        { 
            "name=plot1",
            height = parameters["height"],
            width  = parameters["width"],
            title  = "$(plot_title)",
            title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
            #-------------------------------------------------------------------------
            scale_only_axis   = parameters["scale_only_axis"],
            "axis background/.style={fill=none}",
            line_width        = "{$(parameters["ax_lw"])}",
            tick_style        = "{line width=$(parameters["ax_lw"]),black}",
            ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
            major_tick_length = "{$(parameters["ax_size_major_tick"])}",
            minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
            ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
            "ytick pos = left",
            # "every tick label/.append style={scale=1.5}",
            "every axis plot/.style"="{
                    smooth,
                    mark options={scale=$(parameters["ax_plot_mark_scale"])},
                    line width=$(parameters["ax_plot_line_width"])}",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$E - E_{F}$ (eV)",
            #Legend style
            "every axis legend/.style" = "{
                                            cells={anchor=center},
                                            inner xsep=1pt,
                                            inner ysep=1pt,
                                            nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                            draw=none,
                                            fill=white,
                                            at={$(parameters["ax_legend_position"])},
                                            anchor=south east,
                                           }",
        },
         #spin Up
        [Plot({red,no_marks,forget_plot},Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
        Plot({red,no_marks},Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
        LegendEntry(L"\color{red}{Spin $\uparrow$}"),
        #fermi level
        Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
        #spin Down
        [Plot({blue,no_marks,forget_plot},Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
        Plot({blue,no_marks},Table("x"=>bands[2,:,1],"y"=>bands[2,:,parameters["final_band"]])),
        LegendEntry(L"\color{blue}{Spin $\downarrow$}")
        ),
Axis(
    {
        "anchor = south west",
        "at={(plot1.south east)}",
        height = parameters["height"],
        width  = parameters["ax_width_plotwdos"],
        "axis background/.style={fill=none}",
        "axis line style" = "{line width=$(parameters["ax_lw"])}",
        "clip mode = individual",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"]),rotate=180}",
        xlabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        # "axis line style = {line width=2pt}",
        # "clip mode = individual",
         ylabel = L"$E - E_{F}$ (eV)",
        "xlabel = DOS",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)

if build 
    make_dir("build_plots")
    
    name2build = "plot-$(plot_title).pdf"
    pgfsave("build-plots"*"/"*name2build,plot)
    println("$(name2build) has been created!")
end
return plot
end

function plotwdosbubble(dir_calc::String,params::Dict,build::Bool=false)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    dos         = np.array(data["dos"])
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name2plot"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 
    psize = 0.5
    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!")
        println("Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end

    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    plot = @pgf TikzPicture(
    Axis(
        { 
            "name=plot1",
            height = parameters["height"],
            width  = parameters["width"],
            title  = "$(plot_title)",
            title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
            #-------------------------------------------------------------------------
            scale_only_axis   = parameters["scale_only_axis"],
            "axis background/.style={fill=none}",
            line_width        = "{$(parameters["ax_lw"])}",
            tick_style        = "{line width=$(parameters["ax_lw"]),black}",
            ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
            major_tick_length = "{$(parameters["ax_size_major_tick"])}",
            minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
            ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
            "ytick pos = left",
            # "every tick label/.append style={scale=1.5}",
            "every axis plot/.style"="{
                    smooth,
                    mark options={scale=$(parameters["ax_plot_mark_scale"])},
                    line width=$(parameters["ax_plot_line_width"])}",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$E - E_{F}$ (eV)",
            #Legend style
            "every axis legend/.style" = "{
                                            cells={anchor=center},
                                            inner xsep=1pt,
                                            inner ysep=1pt,
                                            nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                            draw=none,
                                            fill=white,
                                            at={$(parameters["ax_legend_position"])},
                                            anchor=south east,
                                           }",
        },
            #spin Up
            #[Plot({ "scatter=true",
            #         "mark=*",
            #         "color=red",
            #         raw"point meta=explicit symbolic",
            #         raw"scatter/@pre marker code/.append style={/tikz/mark size=\pgfplotspointmeta/1}",
            #         raw"scatter/@post marker code/.code={\endscope}",
            #         forget_plot
            #       },Table({"meta=y"},"x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            [Plot({ 
                        "scatter",
                        "scatter src=y",
                        "only marks",
                        "scatter/use mapped color={draw=red,fill=red,fill opacity=0.9}",
                        "mark options={line width=1pt}",
                        raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*3 \as \perpointmarksize}",
                        raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                        # raw"scatter/@pre marker code/.append style={/tikz/mark size=\pgfplotspointmetatransformed/1000}",
                        forget_plot
                    },Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            Plot({ "scatter",
                    "scatter src=y",
                    "only marks",
                    "scatter/use mapped color={draw=red,fill=red,fill opacity=0.9}",
                    "mark options={draw=red,fill=red,line width=1pt}",
                    raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*3 \as \perpointmarksize}",
                    raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                 },Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
            LegendEntry(L"\color{red}{Spin $\uparrow$}"),
            #fermi level
            Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
            #spin Down
            [Plot({ 
                        "scatter",
                        "scatter src=y",
                        "only marks",
                        "scatter/use mapped color={draw=blue,fill=blue,fill opacity=0.5}",
                        "mark options={line width=1pt}",
                        raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*3  \as \perpointmarksize}",
                        raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                        forget_plot
                    },Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            Plot({ "scatter",
                    "mark=*",
                    "only marks",
                    "scatter src=y",
                    "scatter/use mapped color={draw=blue,fill=blue,fill opacity=0.5}",
                    "mark options={draw=blue,fill=blue,line width=1pt}",
                    raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*3 \as \perpointmarksize}",
                    raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                 },Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
            LegendEntry(L"\color{blue}{Spin $\downarrow$}"),
        ),
Axis(
    {
        height = parameters["height"],
        width  = parameters["ax_width_plotwdos"],
        "anchor = south west",
        "at={(plot1.south east)}",
        "axis background/.style={fill=none}",
        "axis line style" = "{line width=$(parameters["ax_lw"])}",
        "clip mode = individual",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"]),rotate=180}",
        xlabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        # "axis line style = {line width=2pt}",
        # "clip mode = individual",
         ylabel = L"$E - E_{F}$ (eV)",
        "xlabel = DOS",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)

if build 
    make_dir("build-plots")
    name2plot = data["name2plot"]
    name2build = "plot-$(name2plot).pdf"
    pgfsave("build-plots"*"/"*name2build,plot)
    println("$(name2build) has been created!")
end
return plot
end

function plotcotinumbands(x::Array,y::Array,color::String="red",scale_point::Integer=3)
    p = @pgf Plot({ 
        "scatter",
        "scatter src=y",
        "only marks",
        "scatter/use mapped color"="{draw=$(color),fill=$(color),fill opacity=0.5}",
        "mark options={line width=1pt}",
        raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*5 \as \perpointmarksize}",
        raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
        # raw"scatter/@pre marker code/.append style={/tikz/mark size=\pgfplotspointmetatransformed/1000}",
        forget_plot
    },Table("x"=>x,"y"=>y))
return p
end

function plotsingleband(x::Array,y::Array,label::String,color::String="blue")
   p=@pgf [ Plot({ "scatter",
                    "scatter src=y",
                    "only marks",
                    "scatter/use mapped color"="{draw=$(color),fill=$(color),fill opacity=0.5}",
                    "mark options"="{draw=$(color),fill=$(color),line width=1pt}",
                    raw"visualization depends on={-(cos(deg(y))*sin(deg(y)))*3 \as \perpointmarksize}",
                    raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                    },Table("x"=>x,"y"=>y)),
                    LegendEntry(L"\color{%$(color)}{%$(label)}")]
return p
end




function plotwdoscom(dir_calc::String,params::Dict,bubble::Bool=false,build::Bool=false)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    dos         = np.array(data["dos"])
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name2plot"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 
    psize = 0.5
    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!")
        println("Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end

    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    plot = @pgf TikzPicture(
    Axis(
        { 
            "name=plot1",
            height = parameters["height"],
            width  = parameters["width"],
            title  = "$(plot_title)",
            title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
            #-------------------------------------------------------------------------
            scale_only_axis   = parameters["scale_only_axis"],
            "axis background/.style={fill=none}",
            line_width        = "{$(parameters["ax_lw"])}",
            tick_style        = "{line width=$(parameters["ax_lw"]),black}",
            ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
            major_tick_length = "{$(parameters["ax_size_major_tick"])}",
            minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
            ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
            "ytick pos = left",
            # "every tick label/.append style={scale=1.5}",
            "every axis plot/.style"="{
                    smooth,
                    mark options={scale=$(parameters["ax_plot_mark_scale"])},
                    line width=$(parameters["ax_plot_line_width"])}",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$E - E_{F}$ (eV)",
            #Legend style
            "every axis legend/.style" = "{
                                            cells={anchor=center},
                                            inner xsep=1pt,
                                            inner ysep=1pt,
                                            nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                            draw=none,
                                            fill=white,
                                            at={$(parameters["ax_legend_position"])},
                                            anchor=south east,
                                           }",
        },

            [plotcotinumbands(bands[1,:,1],bands[1,:,i]) for i in parameters["initial_band"]:parameters["final_band"]],
            plotsingleband(bands[1,:,1],bands[1,:,end],"\\mathrm{Spin }\\uparrow","red"),
            [plotcotinumbands(bands[2,:,1],bands[2,:,i],"blue") for i in parameters["initial_band"]:parameters["final_band"]],
            plotsingleband(bands[2,:,1],bands[2,:,end],"\\mathrm{Spin }\\uparrow","blue")
            
        ),
Axis(
    {
        height = parameters["height"],
        width  = parameters["ax_width_plotwdos"],
        "anchor = south west",
        "at={(plot1.south east)}",
        "axis background/.style={fill=none}",
        "axis line style" = "{line width=$(parameters["ax_lw"])}",
        "clip mode = individual",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"]),rotate=180}",
        xlabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        # "axis line style = {line width=2pt}",
        # "clip mode = individual",
         ylabel = L"$E - E_{F}$ (eV)",
        "xlabel = DOS",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)

if build 
    make_dir("build-plots")
    name2plot = data["name2plot"]
    name2build = "plot-$(name2plot).pdf"
    pgfsave("build-plots"*"/"*name2build,plot)
    println("$(name2build) has been created!")
end
return plot
end







