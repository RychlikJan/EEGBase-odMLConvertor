# -*- coding: utf-8 -*-
"""nixodmlconverter

nixodmlconverter converts odML content between odML and NIX files. The converter
a) imports content from an existing XML formatted odML file and appends it to
a new or existing NIX file. The content of an existing odML file is automatically
converted to the latest odML format before it is imported to the NIX file.
Furthermore, the converter b) exports odML content from a NIX file and saves it
to an XML formatted odML file. If an odML file of the same name exists, the
file will be overwritten.

Usage: nixodmlconverter [-h] FILE...

Arguments:
    FILE            NIX or odML file.

                    If the provided file is a NIX file, the odML content of this NIX file
                    will be exported to an odML file of the same name.
                    Existing odML output files will be overwritten.

                    If the provided file is an XML formatted odML file, the content
                    of this odML file will be imported to a NIX file of the same name.

                    If a NIX file with the same name exists, the content of the odML
                    file will be appended, otherwise, a new NIX file will be created.

                    Multiple files can be provided.

Options:
    -h --help       Show this screen.
    --version       Show version
"""

import os
import sys

from docopt import docopt

import nixio as nix
import odml

from odml.tools.format_converter import VersionConverter
from odml.tools.odmlparser import ODMLReader
from odml.tools.parser_utils import InvalidVersionException

INFO = {"sections read": 0,
        "sections written": 0,
        "properties read": 0,
        "properties written": 0,
        "skipped empty properties": 0,
        "skipped binary values": 0,
        "skipped none values": 0,
        "type errors": 0,
        "mod_prop_values": 0,
        "odml_types_omitted": 0}


def print_info():
    print("\nConversion info")
    print("{sections read}\t Sections were read\n"
          "{sections written}\t Sections were written\n"
          "{properties read}\t Properties were read\n"
          "{properties written}\t Properties were written\n"
          "{skipped empty properties}\t Properties were skipped because they "
          "contained only None or binary values\n"
          "{skipped binary values}\t Values were skipped because they "
          "were of type 'binary'\n"
          "{skipped none values}\t Values were skipped because they were "
          "empty (None)\n"
          "{type errors}\t Type Errors were encountered\n"
          "{mod_prop_values}\t Values were modified due "
          "to unsupported unicode characters\n"
          "{odml_types_omitted}\t Unidentified odml value types omitted "
          "(using string instead)\n".format(**INFO))


def convert_value(val, dtype):
    if dtype == "binary":
        INFO["skipped binary values"] += 1
        return None

    if val is None:
        INFO["skipped none values"] += 1
        return None

    if dtype in ("date", "time", "datetime"):
        val = val.isoformat()

    return val


########### ODML -> NIX ##############

def odml_to_nix_property(odmlprop, nixsec):
    """
    Creates a new Property for a provided NIX Section
    and populates all attributes with the corresponding
    values from a provided odML Property.

    Properties not containing any attributes are ignored.

    :param odmlprop: odml.Property
    :param nixsec: nix.Section
    """
    INFO["properties read"] += 1
    nixvalues = []
    for val in odmlprop.values:
        nixv = convert_value(val, odmlprop.dtype)
        if nixv is not None:
            nixvalues.append(nixv)

    if not nixvalues:
        INFO["skipped empty properties"] += 1
        return

    # We need to get the appropriate NIX DataType for the current odML values
    dtype = nix.DataType.get_dtype(nixvalues[0])

    nixprop = nixsec.create_property(odmlprop.name, dtype, oid=odmlprop.id)

    # Hotfix until nix.Property.values support unicode content
    try:
        nixprop.values = nixvalues
    except UnicodeError:
        enc_vals = []
        for val in nixvalues:
            enc_vals.append(val.encode('utf-8').decode('ascii', 'ignore'))

        print("\n[WARNING] The Property.values currently do not support unicode. "
              "Values will be adjusted: \n{}\n{}\n".format(nixvalues, enc_vals))

        nixprop.values = enc_vals
        INFO["mod_prop_values"] += 1

    # Python2 hotfix, since the omega character is not sanitized
    # in nixpy Property.unit
    try:
        nixprop.unit = odmlprop.unit
    except UnicodeDecodeError:
        if u"Ω" in odmlprop.unit:
            print("\n[WARNING] Property.unit currently does not support the omega "
                  "unicode character. It will be replaced by 'Ohm'.\n")
            nixprop.unit = odmlprop.unit.replace(u"Ω", "Ohm").encode('ascii')

    nixprop.definition = odmlprop.definition
    nixprop.uncertainty = odmlprop.uncertainty
    nixprop.reference = odmlprop.reference
    nixprop.value_origin = odmlprop.value_origin
    nixprop.dependency = odmlprop.dependency
    nixprop.dependency_value = odmlprop.dependency_value

    # We also need to provide the appropriate odML data type for a potential
    # later export from NIX to odML.
    try:
        nixprop.odml_type = nix.property.OdmlType(odmlprop.dtype)
    except ValueError:
        print("\n[WARNING] Cannot set odml type {}\n".format(odmlprop.dtype))
        INFO["odml_types_omitted"] += 1

    INFO["properties written"] += 1


def odml_to_nix_recurse(odmlseclist, nixparentsec):
    for odmlsec in odmlseclist:
        INFO["sections read"] += 1
        secname = odmlsec.name
        definition = odmlsec.definition
        reference = odmlsec.reference
        repository = odmlsec.repository

        nixsec = nixparentsec.create_section(secname, odmlsec.type, oid=odmlsec.id)
        INFO["sections written"] += 1
        nixsec.definition = definition

        if reference is not None:
            nixsec.reference = reference

        if repository is not None:
            nixsec.repository = repository

        for odmlprop in odmlsec.properties:
            odml_to_nix_property(odmlprop, nixsec)
            msg = ("\rProcessed Sections: {}; processed Properties: {}".format(
                INFO['sections read'], INFO['properties read']))
            sys.stdout.write(msg)

        odml_to_nix_recurse(odmlsec.sections, nixsec)


def write_odml_doc(odmldoc, nixfile):
    nixsec = nixfile.create_section('odML document', 'odML document', oid=odmldoc.id)
    INFO["sections written"] += 1
    if odmldoc.author:
        nixsec.create_property('odML author', [odmldoc.author])
    if odmldoc.date:
        nixsec.create_property('odML date', [odmldoc.date.isoformat()])
    if odmldoc.version:
        nixsec.create_property('odML version', [odmldoc.version])
    if odmldoc.repository:
        nixsec.create_property('odML repository', [odmldoc.repository])
    return nixsec


def nixwrite(odml_doc, filename, mode='append'):
    filemode = None
    if mode == 'append' or mode == 'overwrite metadata':
        filemode = nix.FileMode.ReadWrite
    elif mode == 'overwrite':
        filemode = nix.FileMode.Overwrite
    nixfile = nix.File.open(filename, filemode)

    if mode == 'overwrite metadata':
        if 'odML document' in nixfile.sections:
            del nixfile.sections['odML document']

    nix_document_section = write_odml_doc(odml_doc, nixfile)
    odml_to_nix_recurse(odml_doc.sections, nix_document_section)


############### NIX -> ODML #################
#
# def odmlwrite(nix_file, filename):
#     odml_doc, nix_sections = get_odml_doc(nix_file)
#     nix_to_odml_recurse(nix_sections, odml_doc)
#     odml.save(odml_doc, filename)
#
#
# def get_odml_doc(nix_file):
#     """
#     Extracts sections from a provided nix.File and returns sections and
#     a new odml.Document.
#     If the metadata root of the nix.File contains a specific section with the
#     name 'odML document' only the subsections of this section will be returned.
#     Otherwise all sections of the metadata root will be returned.
#
#     :param nix_file: a nix.File
#
#     :return: tuple containing an odml.Document and a list of nix.Sections
#     """
#     if nix_file.find_sections(filtr=lambda x: "odML document" in x.name):
#         doc_section = nix_file.sections['odML document']
#         # generate odml document
#         attributes = ['author', 'version', 'repository', 'date']
#         doc_attributes = {attr: doc_section.props['odML {}'.format(attr)].values[0]
#                           for attr in attributes
#                           if 'odML {}'.format(attr) in doc_section.props}
#         doc_attributes['oid'] = doc_section.id
#
#         doc = odml.Document(**doc_attributes)
#
#     elif nix_file.sections:
#         doc = odml.Document()
#         doc_section = nix_file
#     else:
#         raise ValueError('No exportable sections present in nix file.')
#
#     return doc, doc_section.sections
#
#
# def nix_to_odml_property(nixprop, odml_sec):
#     """
#     Creates a new Property for a provided odml Section
#     and populates all attributes with the corresponding
#     values from a provided nix Property.
#
#     :param nixprop: nix.Property
#     :param odml_sec: odml.Section
#     """
#     INFO["properties read"] += 1
#
#     # extract and convert property attributes from nix
#     prop_attributes = ['name', 'values', 'unit', 'uncertainty', 'reference',
#                        'definition', 'dependency', 'dependency_value',
#                        'odml_type', 'value_origin', 'id']
#
#     nix_prop_attributes = {attr: getattr(nixprop, attr)
#                            for attr in prop_attributes if hasattr(nixprop, attr)}
#
#     if 'id' in nix_prop_attributes:
#         nix_prop_attributes['oid'] = nix_prop_attributes.pop('id')
#
#     if 'odml_type' in nix_prop_attributes:
#         nix_prop_attributes['dtype'] = nix_prop_attributes.pop('odml_type').value
#
#     nix_prop_attributes['parent'] = odml_sec
#     nix_prop_attributes['value'] = list(nix_prop_attributes.pop('values'))
#
#     odml.Property(**nix_prop_attributes)
#     INFO["properties written"] += 1
#
#
# def nix_to_odml_recurse(nix_section_list, odml_section):
#     for nix_sec in nix_section_list:
#         INFO["sections read"] += 1
#
#         # extract and convert section attributes from nix
#         attributes = ['name', 'type', 'definition', 'reference',
#                       'repository', 'link', 'id']
#         nix_attributes = {attr: getattr(nix_sec, attr) for attr in attributes if
#                           hasattr(nix_sec, attr)}
#         nix_attributes['parent'] = odml_section
#         if 'id' in nix_attributes:
#             nix_attributes['oid'] = nix_attributes.pop('id')
#
#         odml_sec = odml.Section(**nix_attributes)
#         INFO["sections written"] += 1
#         for nixprop in nix_sec.props:
#             nix_to_odml_property(nixprop, odml_sec)
#
#         nix_to_odml_recurse(nix_sec.sections, odml_sec)
#

def convert(filename, mode='append'):
    # Determine input and output format
    file_base, file_ext = os.path.splitext(filename)
    if file_ext in ['.xml', '.odml']:
        output_format = '.nix'
    elif file_ext in ['.nix']:
        output_format = '.xml'
    else:
        raise ValueError('Unknown file format {}'.format(file_ext))

    # odML files can not be appended but only be overwritten
    if mode != 'overwrite' and output_format in ['.xml', '.odml']:
        mode = 'overwrite'

    # Check output file
    outfilename = file_base + output_format
    if os.path.exists(outfilename):
        # yesno = user_input("File {} already exists. "
        #                    "{} (y/n)? ".format(outfilename, mode.title()))
        #
        yesno = "y"
        if yesno.lower() not in ("y", "yes"):
            print("Aborted")
            return

    # Load, convert and save to new format
    print("Saving to {} file... ".format(output_format))
    if output_format in ['.nix']:
        try:
            odml_doc = odml.load(filename)
        except InvalidVersionException:

            # yesno = user_input("odML file format version is outdated. "
            #                    "Automatically convert {} to the latest version "
            #                    "(y/n)? ".format(outfilename))
            yesno = "y"
            if yesno.lower() not in ("y", "yes"):
                print("  Use the odml.tools.VersionConverter to convert "
                      "to the latest odML file version.")
                print("  Aborted")
                return

            xml_string = VersionConverter(filename).convert()
            odml_doc = ODMLReader().from_string(xml_string)

        nixwrite(odml_doc, outfilename, mode=mode)

    elif output_format in ['.xml', '.odml']:
        nix_file = nix.File.open(filename, nix.FileMode.ReadOnly)
        # odmlwrite(nix_file, outfilename)
    else:
        raise ValueError('Unknown file format {}'.format(output_format))

    print("\nDone")


def main(args=None):
    parser = docopt(__doc__, argv=args, version="0.0.4")

    files = parser['FILE']
    print(files)
    for curr_file in files:
        convert(curr_file)
    print_info()


if __name__ == "__main__":
    main(sys.argv[1:])
