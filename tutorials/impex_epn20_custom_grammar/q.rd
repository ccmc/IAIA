<?xml version="1.0" encoding="utf-8"?>

<resource schema="impex">
   <meta name="title">IMPEx Simulation Data</meta>
   <meta name="creationDate">2016-04-28T12:00:00Z</meta>
   <meta name="description" format="plain">
      IMPEx simulation runs provided by FMI, LATMOS and SINP
   </meta>
   <meta name="copyright">Free to use.</meta>
   <meta name="creator.name">IMPEx-FP7 Project Team, Tarek Al-Ubaidi</meta>
   <meta name="subject">Simulated Pplasma environments of solar system objects</meta>

    <table id="epn_core" onDisk="True" adql="True" primary="granule_uid">
        <mixin
          optional_columns="access_estsize access_url access_format file_name publisher"
          spatial_frame_type="body"
        >//epntap2#table-2_0</mixin>
        <meta name="description">IMPEx Simulation Data</meta>
        <meta name="referenceURL">http://impex-fp7.oeaw.ac.at/</meta>
    </table>

    <data id="impex_epn20">
        <sources>
        	<item>http://impex-portal.oeaw.ac.at/config?fmt=xml</item>
        </sources>
        <customGrammar module="res/fetchandform"/>

        <make table="epn_core">
            <rowmaker id="build_impex_epn20" idmaps="*">
                <apply procDef="//epntap2#populate-2_0" name="epnpop">
                    <bind key="time_exp_min">parseWithNull(@time_exp_min, float, "9999.9999")</bind>
                    <bind key="time_exp_max">parseWithNull(@time_exp_max, float, "9999.9999")</bind>
                    <bind key="time_min">parseWithNull(@time_min, float, "9999.9999")</bind>
                    <bind key="time_max">parseWithNull(@time_max, float, "9999.9999")</bind>
                    <bind key="time_sampling_step_min">parseWithNull(@time_exp_max, float, "9999.9999")</bind>
                    <bind key="time_sampling_step_max">parseWithNull(@time_exp_max, float, "9999.9999")</bind>
                    <bind key="spectral_range_min">parseWithNull(@spectral_range_min, float, "9999.9999")</bind>
                    <bind key="spectral_range_max">parseWithNull(@spectral_range_max, float, "9999.9999")</bind>
                    <bind key="spectral_sampling_step_min">parseWithNull(@spectral_sampling_step_min, float, "9999.9999")</bind>
                    <bind key="spectral_sampling_step_max">parseWithNull(@spectral_sampling_step_max, float, "9999.9999")</bind>
                    <bind key="spectral_resolution_min">parseWithNull(@spectral_resolution_min, float, "9999.9999")</bind>
                    <bind key="spectral_resolution_max">parseWithNull(@spectral_resolution_max, float, "9999.9999")</bind>
                    <bind key="c1min">parseWithNull(@c1min, float, "9999.9999")</bind>
                    <bind key="c1max">parseWithNull(@c1max, float, "9999.9999")</bind>
                    <bind key="c2min">parseWithNull(@c2min, float, "9999.9999")</bind>
                    <bind key="c2max">parseWithNull(@c2max, float, "9999.9999")</bind>
                    <bind key="c3min">parseWithNull(@c3min, float, "9999.9999")</bind>
                    <bind key="c3max">parseWithNull(@c3max, float, "9999.9999")</bind>
                    <bind key="incidence_min">parseWithNull(@incidence_min, float, "9999.9999")</bind>
                    <bind key="incidence_max">parseWithNull(@incidence_max, float, "9999.9999")</bind>
                    <bind key="emergence_min">parseWithNull(@emergence_min, float, "9999.9999")</bind>
                    <bind key="emergence_max">parseWithNull(@emergence_max, float, "9999.9999")</bind>
                    <bind key="phase_min">parseWithNull(@phase_min, float, "9999.9999")</bind>
                    <bind key="phase_max">parseWithNull(@phase_max, float, "9999.9999")</bind>
                    <bind key="s_region">parseWithNull(@s_region, str, "NULL")</bind>
                    <bind key="instrument_host_name">parseWithNull(@s_region, str, "NULL")</bind>
                    <bind key="instrument_name">parseWithNull(@s_region, str, "NULL")</bind>
                    <bind key="spatial_frame_type">parseWithNull(@spatial_frame_type, str, "NULL")</bind>
                    <bind key="granule_uid">@granule_uid</bind>
                    <bind key="granule_gid">@granule_gid</bind>
                    <bind key="obs_id">@obs_id</bind>
                    <bind key="target_name">"simulated"</bind>
                    <bind key="processing_level">5</bind>
                </apply>
                <map key="file_name">parseWithNull(@file_name, str, "NULL")</map>
            </rowmaker>         
        </make>
    </data>
</resource>
